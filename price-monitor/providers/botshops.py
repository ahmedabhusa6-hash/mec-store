"""Bot-shop reseller adapters — 7 providers whose API keys were issued to the
owner's Telegram account (verified live 2026-10-13, read-only probes only).

Sources of truth (docs / live responses, all archived under research/tg_si/):
  stackvault  @stackvault_bot    https://decohomz.com/reseller-api/v1  (docs: stackvault.shop/docs)
                                 Bearer svr_... | GET /balance {ok,balance,name} | GET /products {ok,products[]}
  prodseller  @ProdSellerBot     https://prodseller.com/v1
                                 X-API-Key psk_... | GET /balance | GET /products {products[]}
  acczone     @Acczone_Store_bot https://api.acczone.xyz  (FastAPI openapi.json archived)
                                 ?apikey= query | GET /getBalance | GET /getServices [{key,name,price,is_active}]
  aivaulthub  @Gemini_Shop_Robot https://reseller.aivaulthub.store/api/v1  (docs /api/v1/docs)
                                 X-API-Key rsk_... | GET /me | GET /products {currency,rate,products[{service_id,pricing_tiers}]}
  richai      @RichAIStoreBot    https://cgpt-active.pro/telegram/api/v1  (docs /telegram/api/docs)
                                 Bearer rsk_... | GET /me | GET /products {products[{your_unit_price,retail_price,stock}]}
  aiversex    @AIVerseXBot       https://aiversehub.store/api/v1
                                 X-API-Key AK_... | GET /me | GET /products {services[{service_id,price,stock}]}
  digitalcore @DCoreStoreBot     https://digitalcore.top/api/user  (docs digitalcore.top/docs)
                                 Api-Key header | GET /me {balance,total_orders} | GET /products [..]

Read-only policy (master prompt): catalog + balance ONLY. Order endpoints
(/orders, /buy, POST anything) are NEVER called by this platform.

aixpress (@AIXpress_Bot, key AK_...) is NOT implemented: its documented base
aiversehub.store rejects the key (401) and aixpress.shop is unreachable —
registered as BLOCKED pending provider recovery.
"""
from .base import ProviderAdapter, ProviderError


def _f(v):
    """Tolerant float: handles 'None', '0.4', 0, None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s.lower() in ("none", "null", ""):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _stock_int(v):
    n = _f(v)
    return int(n) if n is not None else None


class _ApiKeyAdapter(ProviderAdapter):
    """Shared skeleton: static key auth verified by a lightweight GET."""
    code = None
    BASE = None
    AUTH_HEADER = None          # e.g. {"X-API-Key": key} or {"Api-Key": key}
    CRED_ENV = None             # e.g. "STACKVAULT_API_KEY"
    VERIFY_PATH = "/balance"    # auth verification endpoint (read-only)

    def credentials_present(self):
        return bool(self.creds.get(self.CRED_ENV))

    def _key(self):
        return self.creds[self.CRED_ENV]

    def _headers(self):
        h = {}
        for kk, vv in (self.AUTH_HEADER or {}).items():
            h[kk] = vv.format(key=self._key())
        return h

    def authenticate(self):
        """Verify the key with a read-only GET; cache as bearer-style token."""
        res = self.call("GET", self.BASE + self.VERIFY_PATH,
                        headers=self._headers(), timeout=self.AUTH_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        if res.status == 200 and body.get("ok") is False:
            raise ProviderError("auth rejected: " + str(body)[:120])
        self.token = self._key()
        self.token_exp = 3600
        return True

    # subclasses implement fetch_catalog / fetch_balance using _headers()


# ---------------- StackVault ----------------
class StackVaultAdapter(_ApiKeyAdapter):
    code = "stackvault"
    BASE = "https://decohomz.com/reseller-api/v1"
    AUTH_HEADER = {"Authorization": "Bearer {key}"}
    CRED_ENV = "STACKVAULT_API_KEY"

    def fetch_catalog(self):
        res = self.call("GET", self.BASE + "/products", headers=self._headers(),
                        timeout=self.CALL_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        prods = body.get("products") or []
        rows = []
        for p in prods:
            stock = _stock_int(p.get("stock"))
            rows.append({
                "external_id": str(p.get("id")),
                "product_name": p.get("name") or "",
                "brand": p.get("category"),
                "region": None,
                "currency": "USD",
                "unit_price": _f(p.get("price")),
                "discount_pct": None,
                "unit_cost": None,
                "stock": stock if stock is not None else ("IN_STOCK" if p.get("in_stock") else "OUT_OF_STOCK"),
                "status": "ACTIVE" if p.get("in_stock", True) else "INACTIVE",
                "raw": {"id": p.get("id"), "category_id": p.get("category_id"),
                        "price": p.get("price"), "stock": p.get("stock")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", self.BASE + "/balance", headers=self._headers())
        b = res.body if isinstance(res.body, dict) else {}
        bal = _f(b.get("balance"))
        return {"balance": bal, "currency": "USD", "name": b.get("name")} if bal is not None else None


# ---------------- ProdSeller ----------------
class ProdSellerAdapter(_ApiKeyAdapter):
    code = "prodseller"
    BASE = "https://prodseller.com/v1"
    AUTH_HEADER = {"X-API-Key": "{key}"}
    CRED_ENV = "PRODSELLER_API_KEY"

    def fetch_catalog(self):
        res = self.call("GET", self.BASE + "/products", headers=self._headers(),
                        timeout=self.CALL_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        prods = body.get("products") or []
        rows = []
        for p in prods:
            price = _f(p.get("price"))
            public = _f(p.get("publicPrice"))
            disc = None
            if price is not None and public and public > price > 0:
                disc = round((1 - price / public) * 100, 2)
            rows.append({
                "external_id": str(p.get("id")),
                "product_name": p.get("name") or "",
                "brand": None,
                "region": None,
                "currency": "USD",
                "unit_price": price,
                "discount_pct": disc,
                "unit_cost": None,
                "stock": "IN_STOCK" if p.get("inStock") else "OUT_OF_STOCK",
                "status": "ACTIVE" if p.get("inStock") else "INACTIVE",
                "raw": {"id": p.get("id"), "publicPrice": p.get("publicPrice"),
                        "delivery": p.get("delivery"), "sold": p.get("sold"),
                        "requiresEmailActivation": p.get("requiresEmailActivation")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", self.BASE + "/balance", headers=self._headers())
        b = res.body if isinstance(res.body, dict) else {}
        bal = _f(b.get("balance"))
        return {"balance": bal, "currency": "USD",
                "membership": b.get("membership")} if bal is not None else None


# ---------------- Acczone ----------------
class AcczoneAdapter(_ApiKeyAdapter):
    code = "acczone"
    BASE = "https://api.acczone.xyz"
    AUTH_HEADER = {}            # auth via query param
    CRED_ENV = "ACCZONE_API_KEY"
    VERIFY_PATH = "/getBalance"

    def _url(self, path):
        return f"{self.BASE}{path}?apikey={self._key()}"

    def authenticate(self):
        res = self.call("GET", self._url(self.VERIFY_PATH), timeout=self.AUTH_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        if res.status != 200 or "apikey" not in body:
            raise ProviderError(f"auth verify failed: HTTP {res.status}")
        self.token = self._key()
        self.token_exp = 3600
        return True

    def fetch_catalog(self):
        res = self.call("GET", self._url("/getServices"), timeout=self.CALL_TIMEOUT)
        services = res.body if isinstance(res.body, list) else []
        rows = []
        for s in services:
            active = bool(s.get("is_active"))
            rows.append({
                "external_id": str(s.get("key")),
                "product_name": s.get("name") or "",
                "brand": None,
                "region": None,
                "currency": "USD",
                "unit_price": _f(s.get("price")),
                "discount_pct": None,
                "unit_cost": None,
                "stock": "UNKNOWN",
                "status": "ACTIVE" if active else "INACTIVE",
                "raw": {"key": s.get("key"), "price": s.get("price"),
                        "is_active": s.get("is_active")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", self._url("/getBalance"))
        b = res.body if isinstance(res.body, dict) else {}
        bal = _f(b.get("balance"))
        return {"balance": bal, "currency": "USD",
                "username": b.get("username")} if bal is not None else None


# ---------------- AIVaultHub (Gemini Shop) ----------------
class AivaulthubAdapter(_ApiKeyAdapter):
    code = "aivaulthub"
    BASE = "https://reseller.aivaulthub.store/api/v1"
    AUTH_HEADER = {"X-API-Key": "{key}"}
    CRED_ENV = "AIVAULTHUB_API_KEY"
    VERIFY_PATH = "/me"

    def fetch_catalog(self):
        res = self.call("GET", self.BASE + "/products", headers=self._headers(),
                        timeout=self.CALL_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        prods = body.get("products") or []
        rows = []
        for p in prods:
            tiers = p.get("pricing_tiers") or []
            price = _f(tiers[0].get("price")) if tiers else None
            stock = _stock_int(p.get("stock"))
            rows.append({
                "external_id": str(p.get("service_id")),
                "product_name": p.get("name") or "",
                "brand": None,
                "region": None,
                "currency": body.get("currency") or "USD",
                "unit_price": price,
                "discount_pct": None,
                "unit_cost": None,
                "stock": stock if stock is not None else "UNKNOWN",
                "status": "ACTIVE" if (stock or 0) > 0 else "INACTIVE",
                "raw": {"service_id": p.get("service_id"),
                        "pricing_tiers": tiers[:3], "rate": body.get("rate")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", self.BASE + "/me", headers=self._headers())
        b = res.body if isinstance(res.body, dict) else {}
        bal = _f(b.get("balance"))
        return {"balance": bal, "currency": b.get("currency") or "USD"} if bal is not None else None


# ---------------- AIVerseX ----------------
class AiversexAdapter(_ApiKeyAdapter):
    code = "aiversex"
    BASE = "https://aiversehub.store/api/v1"
    AUTH_HEADER = {"X-API-Key": "{key}"}
    CRED_ENV = "AIVERSEX_API_KEY"
    VERIFY_PATH = "/me"

    def fetch_catalog(self):
        res = self.call("GET", self.BASE + "/products", headers=self._headers(),
                        timeout=self.CALL_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        services = body.get("services") or body.get("products") or []
        rows = []
        for s in services:
            stock = _stock_int(s.get("stock"))
            rows.append({
                "external_id": str(s.get("service_id")),
                "product_name": s.get("name") or "",
                "brand": None,
                "region": None,
                "currency": "USD",
                "unit_price": _f(s.get("price")),
                "discount_pct": None,
                "unit_cost": None,
                "stock": stock if stock is not None else "UNKNOWN",
                "status": "ACTIVE" if (stock or 0) > 0 else "INACTIVE",
                "raw": {"service_id": s.get("service_id"), "price": s.get("price")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", self.BASE + "/me", headers=self._headers())
        b = res.body if isinstance(res.body, dict) else {}
        bal = _f(b.get("wallet_balance") or b.get("balance"))
        return {"balance": bal, "currency": "USD"} if bal is not None else None


# ---------------- RichAI ----------------
class RichAIAdapter(_ApiKeyAdapter):
    code = "richai"
    BASE = "https://cgpt-active.pro/telegram/api/v1"
    AUTH_HEADER = {"Authorization": "Bearer {key}"}
    CRED_ENV = "RICHAI_API_KEY"
    VERIFY_PATH = "/me"

    def fetch_catalog(self):
        res = self.call("GET", self.BASE + "/products", headers=self._headers(),
                        timeout=self.CALL_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        prods = body.get("products") or []
        rows = []
        for p in prods:
            stock = _stock_int(p.get("stock"))
            retail = _f(p.get("retail_price"))
            unit = _f(p.get("your_unit_price"))
            disc = None
            if unit is not None and retail and retail > unit > 0:
                disc = round((1 - unit / retail) * 100, 2)
            rows.append({
                "external_id": str(p.get("id")),
                "product_name": p.get("name") or "",
                "brand": None,
                "region": None,
                "currency": "USD",
                "unit_price": unit,
                "discount_pct": disc,
                "unit_cost": None,
                "stock": stock if stock is not None else "UNKNOWN",
                "status": "ACTIVE" if (stock is None or stock > 0) else "INACTIVE",
                "raw": {"slug": p.get("slug"), "product_type": p.get("product_type"),
                        "retail_price": p.get("retail_price")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", self.BASE + "/me", headers=self._headers())
        b = res.body if isinstance(res.body, dict) else {}
        bal = _f(b.get("balance"))
        return {"balance": bal, "currency": "USD",
                "reseller_id": b.get("reseller_id")} if bal is not None else None


# ---------------- AIXpress (dead key — honest feedback path) ----------------
class AixpressAdapter(AiversexAdapter):
    """Same hub software as aiversex but the aixpress-issued key is REJECTED
    (401 on aiversehub.store, verified 2026-10-13) and aixpress.shop is down.
    Adapter exists so the engine reports a truthful AUTH_FAILED instead of a
    silent skip; will start working as-is if the provider recovers the key."""
    code = "aixpress"
    BASE = "https://aiversehub.store/api/v1"
    CRED_ENV = "AIXPRESS_API_KEY"


# ---------------- DigitalCore ----------------
class DigitalCoreAdapter(_ApiKeyAdapter):
    code = "digitalcore"
    BASE = "https://digitalcore.top/api/user"
    AUTH_HEADER = {"Api-Key": "{key}"}
    CRED_ENV = "DIGITALCORE_API_KEY"
    VERIFY_PATH = "/me"

    def fetch_catalog(self):
        res = self.call("GET", self.BASE + "/products", headers=self._headers(),
                        timeout=self.CALL_TIMEOUT)
        prods = res.body if isinstance(res.body, list) else []
        rows = []
        for p in prods:
            stock = _stock_int(p.get("stock"))
            rows.append({
                "external_id": str(p.get("id")),
                "product_name": p.get("name") or "",
                "brand": None,
                "region": None,
                "currency": "USD",
                "unit_price": _f(p.get("price")),
                "discount_pct": None,
                "unit_cost": _f(p.get("priceFrom")),
                "stock": stock if stock is not None else "UNKNOWN",
                "status": "ACTIVE" if (stock or 0) > 0 else "INACTIVE",
                "raw": {"id": p.get("id"), "price": p.get("price"),
                        "priceFrom": p.get("priceFrom")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", self.BASE + "/me", headers=self._headers())
        b = res.body if isinstance(res.body, dict) else {}
        bal = _f(b.get("balance"))
        return {"balance": bal, "currency": "USD",
                "total_orders": b.get("total_orders")} if bal is not None else None
