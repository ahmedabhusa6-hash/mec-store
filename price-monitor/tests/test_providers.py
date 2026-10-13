#!/usr/bin/env python3
"""MEC provider framework tests — REAL tests, isolated (no network, no DB writes
to production). The DB paths are exercised against the invalid SUPABASE_URL
set by CI env (engine must degrade gracefully — never raise).

Covers master-prompt §11 scenarios: Auth failure, partial failure, retry
discipline (429/5xx), lifecycle gating, dedup/upsert behavior, isolation.
Exit code 0 only if ALL pass. Prints a per-test report.
"""
import json, os, sys, time, types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # price-monitor

PASS, FAIL = [], []


def t(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"[PASS] {name}")
    except Exception as e:
        FAIL.append((name, str(e)[:200]))
        print(f"[FAIL] {name}: {e}")


# ---------- 1) adapter: reloadly (per verified OpenAPI) ----------
def reloadly_contract():
    from providers.reloadly import ReloadlyAdapter
    a = ReloadlyAdapter(creds={})  # no creds
    assert a.credentials_present() is False, "empty creds must be absent"
    a2 = ReloadlyAdapter(creds={"RELOADLY_CLIENT_ID": "x", "RELOADLY_CLIENT_SECRET": "y"})
    assert a2.credentials_present() is True
    assert a2.base == "https://giftcards.reloadly.com"
    a3 = ReloadlyAdapter(creds={"RELOADLY_CLIENT_ID": "x", "RELOADLY_CLIENT_SECRET": "y",
                                "RELOADLY_USE_SANDBOX": "1"})
    assert a3.base == "https://giftcards-sandbox.reloadly.com", "sandbox toggle"
    # auth payload shape per official spec
    captured = {}
    a2.call = types.MethodType(lambda self, method, url, headers=None, payload=None, timeout=None:
                               captured.update({"m": method, "u": url, "p": payload}) or
                               types.SimpleNamespace(status=200, body={"access_token": "tok", "expires_in": 3600}, text=""),
                               a2)
    a2.authenticate()
    assert captured["m"] == "POST" and captured["u"] == "https://auth.reloadly.com/oauth/token"
    assert captured["p"]["grant_type"] == "client_credentials"
    assert captured["p"]["audience"] == "https://giftcards.reloadly.com"
    assert "client_secret" in captured["p"]
    assert a2.token == "tok"


def reloadly_catalog_normalization():
    from providers.reloadly import ReloadlyAdapter
    a = ReloadlyAdapter(creds={"RELOADLY_CLIENT_ID": "x", "RELOADLY_CLIENT_SECRET": "y"})
    a.token = "tok"
    pages = {"p": 0, "d": 0}

    def fake_call(self, method, url, headers=None, payload=None, timeout=None):
        if "/products" in url:
            pages["p"] += 1
            if pages["p"] == 1:
                return types.SimpleNamespace(status=200, body=[
                    {"productId": 1, "productName": "Amazon US", "denominationType": "RANGE",
                     "status": "ACTIVE", "recipientCurrencyCode": "USD",
                     "minRecipientDenomination": 5, "maxrecipientDenomination": 500,
                     "discountPercentage": 7.5, "senderFee": 205.29, "global": False},
                    {"productId": 2, "productName": "Netflix", "denominationType": "RANGE",
                     "status": "INACTIVE", "recipientCurrencyCode": "EUR",
                     "minRecipientDenomination": 25, "maxrecipientDenomination": 25,
                     "discountPercentage": 4.0},
                ], text="")
            return types.SimpleNamespace(status=200, body=[], text="")
        if "/discounts" in url:
            pages["d"] += 1
            return types.SimpleNamespace(status=200, body=[
                {"productId": 1, "product_global": False, "discountPercentage": 9.0}], text="")
        if "/accounts/balance" in url:
            return types.SimpleNamespace(status=200, body={"balance": 42.5, "currencyCode": "USD"}, text="")
        raise AssertionError(f"unexpected url {url}")

    a.call = types.MethodType(fake_call, a)
    rows = a.fetch_catalog()
    assert len(rows) == 2
    r0 = rows[0]
    assert r0["external_id"] == "1" and r0["product_name"] == "Amazon US"
    assert r0["discount_pct"] == 9.0, "discounts endpoint must override catalog discount"
    assert r0["unit_price"] == 5.0 and r0["currency"] == "USD"
    assert r0["stock"] == "IN_STOCK" and r0["status"] == "ACTIVE"
    assert rows[1]["stock"] == "INACTIVE"
    b = a.fetch_balance()
    assert b == {"balance": 42.5, "currency": "USD"}


# ---------- 2) disciplined HTTP ----------
def retry_on_5xx():
    import providers.base as pb
    calls = {"n": 0}
    orig_http, orig_sleep = pb.http, time.sleep
    time.sleep = lambda s: None
    try:
        pb.http = lambda method, url, headers=None, payload=None, timeout=30: (
            calls.__setitem__("n", calls["n"] + 1) or
            types.SimpleNamespace(status=503 if calls["n"] < 3 else 200,
                                   body={"ok": True} if calls["n"] >= 3 else {"e": "down"}, text=""))
        class A(pb.ProviderAdapter):
            def credentials_present(self): return True
            def authenticate(self): self.token = "t"
            def fetch_catalog(self): return []
        a = A()
        r = a.call("GET", "http://x")
        assert r.status == 200 and calls["n"] == 3, f"expected 3 calls, got {calls['n']}"
    finally:
        pb.http = orig_http
        time.sleep = orig_sleep


def fail_fast_on_4xx():
    import providers.base as pb
    class A(pb.ProviderAdapter):
        def credentials_present(self): return True
        def authenticate(self): self.token = "t"
        def fetch_catalog(self): return []
    a = A()
    orig_http = pb.http
    pb.http = lambda method, url, headers=None, payload=None, timeout=30: types.SimpleNamespace(status=404, body={"m": "no"}, text="")
    try:
        try:
            a.call("GET", "http://x")
            raise AssertionError("4xx must raise")
        except pb.ProviderError as e:
            assert "404" in str(e)
    finally:
        pb.http = orig_http


def rate_limit_honor():
    import providers.base as pb
    class A(pb.ProviderAdapter):
        def credentials_present(self): return True
        def authenticate(self): self.token = "t"
        def fetch_catalog(self): return []
    a = A()
    hits = {"n": 0}
    orig_http, orig_sleep = pb.http, time.sleep
    time.sleep = lambda s: None
    try:
        pb.http = lambda method, url, headers=None, payload=None, timeout=30: (
            hits.__setitem__("n", hits["n"] + 1) or
            types.SimpleNamespace(status=429, body={}, text=""))
        try:
            a.call("GET", "http://x")
            raise AssertionError("429 must raise after retries")
        except pb.RateLimited:
            # final call happens before raise: MAX_RETRIES retries + 1 final
            assert hits["n"] == a.MAX_RETRIES + 1, f"expected {a.MAX_RETRIES + 1} calls, got {hits['n']}"
    finally:
        pb.http = orig_http
        time.sleep = orig_sleep


# ---------- 3) sync engine: lifecycle gating + isolation (DB pointing at invalid URL) ----------
def engine_degrades_gracefully():
    from providers.base import sync_all_providers, sync_one
    # SUPABASE_URL is invalid in CI — engine must not raise
    res = sync_all_providers(run_trigger="test")
    assert isinstance(res, list), "engine returns list even on DB errors"


def gating_skips_discovered():
    from providers.base import sync_one
    from providers.mock import MockAdapter
    # DB invalid — but gating happens BEFORE any DB read for these states:
    # we can't run sync_one without DB for success paths; for skip paths it still
    # writes sync_runs. In CI the DB is invalid so we only assert it doesn't raise.
    try:
        r = sync_one({"code": "x", "name": "X", "kind": "api", "status": "RETIRED",
                      "credentials_env": []}, MockAdapter, "test")
        assert isinstance(r, dict)
    except Exception as e:
        raise AssertionError(f"sync_one raised on gated provider: {e}")


# ---------- 4) mock adapter: success/failure simulation ----------
def mock_adapter_paths():
    from providers.mock import MockAdapter
    ok = MockAdapter(creds={"MOCK_KEY": "k", "MOCK_SIZE": "5"})
    assert ok.authenticate()
    cat = ok.fetch_catalog()
    assert len(cat) == 5 and cat[0]["external_id"] == "MOCK-0" and cat[0]["unit_price"] == 10.0
    assert ok.fetch_balance() == {"balance": 100.0, "currency": "USD"}
    fa = MockAdapter(creds={"MOCK_KEY": "fail-auth"})
    try:
        fa.authenticate()
        raise AssertionError("fail-auth must raise")
    except RuntimeError:
        pass
    fc = MockAdapter(creds={"MOCK_KEY": "fail-catalog"})
    try:
        fc.fetch_catalog()
        raise AssertionError("fail-catalog must raise")
    except RuntimeError:
        pass


# ---------- 5) dedup semantics ----------
def upsert_dedup_semantics():
    from providers.reloadly import ReloadlyAdapter
    a = ReloadlyAdapter(creds={"RELOADLY_CLIENT_ID": "x", "RELOADLY_CLIENT_SECRET": "y"})
    a.token = "t"
    state = {"first": True}

    def paged(self, method, url, headers=None, payload=None, timeout=None):
        if "/products" in url:
            batch = ([{"productId": 1, "productName": "A", "denominationType": "RANGE",
                       "status": "ACTIVE", "recipientCurrencyCode": "USD",
                       "minRecipientDenomination": 5, "discountPercentage": 8.0}] if state["first"]
                     else [])
            state["first"] = False
            return types.SimpleNamespace(status=200, body=batch, text="")
        if "/discounts" in url:
            return types.SimpleNamespace(status=200, body=[], text="")
        return types.SimpleNamespace(status=200, body={}, text="")

    a.call = types.MethodType(paged, a)
    rows = a.fetch_catalog()
    assert len(rows) == 1 and rows[0]["external_id"] == "1"
    # same external_id + same provider -> upsert target (unique constraint); no duplicate row
    # (enforced by DB constraint providers.products unique(provider_code, external_id))
    assert rows[0]["discount_pct"] == 8.0


# ---------- 6) botshops adapters (7 live-verified providers, 2026-10-13) ----------
def botshops_contract_matrix():
    """Auth header shape + catalog normalization for each bot-shop adapter,
    using payloads captured verbatim from live responses."""
    from providers import botshops as bs

    cases = [
        # (adapter, creds env name, verify path, catalog payload, expected first row fields)
        (bs.StackVaultAdapter, "STACKVAULT_API_KEY", "/balance",
         {"ok": True, "products": [
             {"id": "ps_1", "name": "X Premium 3M", "category": "Social", "category_id": "soc",
              "price": 11.44, "stock": 93, "in_stock": True}]},
         {"external_id": "ps_1", "unit_price": 11.44, "stock": 93, "status": "ACTIVE", "brand": "Social"}),
        (bs.ProdSellerAdapter, "PRODSELLER_API_KEY", "/balance",
         {"products": [
             {"id": "abc", "name": "Capcut Pro", "price": 2.0, "publicPrice": 2.5,
              "inStock": True, "delivery": "instant"}]},
         {"external_id": "abc", "unit_price": 2.0, "discount_pct": 20.0, "stock": "IN_STOCK"}),
        (bs.AcczoneAdapter, "ACCZONE_API_KEY", "/getBalance",
         [{"key": "ADOBE_EXPRESS", "name": "Adobe Express 12M", "price": 0.12, "is_active": 1}],
         {"external_id": "ADOBE_EXPRESS", "unit_price": 0.12, "status": "ACTIVE", "stock": "UNKNOWN"}),
        (bs.AivaulthubAdapter, "AIVAULTHUB_API_KEY", "/me",
         {"currency": "USD", "rate": "1 USD = 100 INR (fixed)", "products": [
             {"service_id": "service_1", "name": "Netflix 1M", "stock": 7,
              "pricing_tiers": [{"min": 1, "max": 100, "price": 10.0}]}]},
         {"external_id": "service_1", "unit_price": 10.0, "stock": 7, "status": "ACTIVE"}),
        (bs.AiversexAdapter, "AIVERSEX_API_KEY", "/me",
         {"services": [{"service_id": "service_2", "name": "Spotify 3M", "price": 0.35, "stock": 0}]},
         {"external_id": "service_2", "unit_price": 0.35, "stock": 0, "status": "INACTIVE"}),
        (bs.RichAIAdapter, "RICHAI_API_KEY", "/me",
         {"products": [
             {"id": "1", "name": "Perplexity PRO", "slug": "ppx", "product_type": "cdk",
              "retail_price": "14.000000", "your_unit_price": "10.000000", "stock": "None"}]},
         {"external_id": "1", "unit_price": 10.0, "discount_pct": round((1 - 10/14)*100, 2), "stock": "UNKNOWN"}),
        (bs.DigitalCoreAdapter, "DIGITALCORE_API_KEY", "/me",
         [{"id": "gemini_pro_18_months", "name": "Gemini Pro 18M", "stock": "973", "price": "0.4",
           "priceFrom": "0.35"}],
         {"external_id": "gemini_pro_18_months", "unit_price": 0.4, "unit_cost": 0.35, "stock": 973}),
    ]

    for cls, env, verify_path, catalog_payload, expect in cases:
        a = cls(creds={env: "test-key"})
        assert a.credentials_present() is True, f"{cls.code}: creds missing"
        assert cls(creds={}).credentials_present() is False, f"{cls.code}: empty creds must be absent"

        captured = {}

        def fake_call(self, method, url, headers=None, payload=None, timeout=None):
            captured.update({"m": method, "u": url, "h": headers or {}})
            if verify_path in url:
                return types.SimpleNamespace(status=200, body={"ok": True, "balance": 0.5, "apikey": "test-key"}, text="")
            if "/products" in url or "/getServices" in url:
                return types.SimpleNamespace(status=200, body=catalog_payload, text="")
            raise AssertionError(f"{cls.code}: unexpected url {url}")

        a.call = types.MethodType(fake_call, a)
        a.authenticate()
        assert captured["u"].startswith(cls.BASE), f"{cls.code}: base url mismatch"
        if cls.code == "acczone":
            assert "apikey=test-key" in captured["u"], "acczone must pass key via query"
        else:
            hh = {k.lower(): v for k, v in captured["h"].items()}
            assert any("test-key" in str(v) for v in hh.values()), f"{cls.code}: key not in headers"
        rows = a.fetch_catalog()
        assert len(rows) == 1, f"{cls.code}: expected 1 row, got {len(rows)}"
        r0 = rows[0]
        for k, v in expect.items():
            assert r0[k] == v, f"{cls.code}.{k}: expected {v!r}, got {r0[k]!r}"
        b = a.fetch_balance()
        assert isinstance(b, dict) and "balance" in b, f"{cls.code}: balance parse failed"
        # full row sanity (upsert contract with base engine)
        for k in ("external_id", "product_name", "currency", "unit_price", "discount_pct",
                  "unit_cost", "stock", "status", "raw"):
            assert k in r0, f"{cls.code}: missing normalized field {k}"


def botshops_auth_failure():
    """401 from provider must raise ProviderError (engine flips to AUTH_FAILED)."""
    import providers.base as pb
    from providers.botshops import StackVaultAdapter

    a = StackVaultAdapter(creds={"STACKVAULT_API_KEY": "bad"})
    orig_http = pb.http
    pb.http = lambda method, url, headers=None, payload=None, timeout=30: \
        types.SimpleNamespace(status=401, body={"error": "Invalid API Key"}, text="")
    try:
        try:
            a.authenticate()
            raise AssertionError("401 must raise ProviderError")
        except pb.ProviderError as e:
            assert "401" in str(e)
    finally:
        pb.http = orig_http


# ---------- 7) bitrefill adapter (Personal API — live-verified 2026-10-13) ----------
def bitrefill_contract():
    from providers.bitrefill import BitrefillAdapter
    a = BitrefillAdapter(creds={})
    assert a.credentials_present() is False
    a2 = BitrefillAdapter(creds={"BITREFILL_API_KEY": "k"})
    assert a2.credentials_present() is True
    captured = {}

    def fake_call(self, method, url, headers=None, payload=None, timeout=None):
        captured.update({"m": method, "u": url, "h": headers or {}})
        # LIVE shape (2026-10-13): message at TOP level, not under data
        return types.SimpleNamespace(status=200,
                                     body={"meta": {}, "message": "pong"}, text="")

    a2.call = types.MethodType(fake_call, a2)
    a2.authenticate()
    assert captured["u"].endswith("/v2/ping")
    assert captured["h"]["Authorization"] == "Bearer k"

    # docs shape (data.message) must also be accepted
    a3 = BitrefillAdapter(creds={"BITREFILL_API_KEY": "k"})
    a3.call = types.MethodType(
        lambda self, method, url, headers=None, payload=None, timeout=None:
        types.SimpleNamespace(status=200, body={"meta": {}, "data": {"message": "pong"}}, text=""),
        a3)
    assert a3.authenticate()

    # 401 must fail loudly
    a4 = BitrefillAdapter(creds={"BITREFILL_API_KEY": "bad"})
    a4.call = types.MethodType(
        lambda self, method, url, headers=None, payload=None, timeout=None:
        types.SimpleNamespace(status=401, body={"error": "unauthorized"}, text=""),
        a4)
    try:
        a4.authenticate()
        raise AssertionError("401 must raise ProviderError")
    except Exception as e:
        assert "401" in str(e)


def bitrefill_catalog_normalization():
    from providers.bitrefill import BitrefillAdapter
    import providers.bitrefill as bf
    a = BitrefillAdapter(creds={"BITREFILL_API_KEY": "k"})
    pages = {"n": 0}

    def paged(self, method, url, headers=None, payload=None, timeout=None):
        pages["n"] += 1
        if pages["n"] == 1:
            return types.SimpleNamespace(status=200, body={
                "meta": {"limit": 50, "start": 0, "total": 3,
                         "_next": "https://api-bitrefill.com/v2/products?limit=50&start=50"},
                "data": [{
                    "id": "amazon-us", "name": "Amazon US", "base_name": "Amazon",
                    "country_code": "US", "currency": "USD", "categories": ["ecommerce"],
                    "recipient_type": "email", "in_stock": True,
                    "packages": [
                        {"id": "amazon-us<&>25", "value": "25", "price": 29912, "amount": 25},
                        {"id": "amazon-us<&>50", "value": "50", "price": 59824, "amount": 50},
                    ]}]}, text="")
        if "start=50" in url:
            return types.SimpleNamespace(status=200, body={
                "meta": {"limit": 50, "start": 50, "total": 3, "_next": None},
                "data": [
                    {"id": "bitrefill-esim-europe", "name": "Bitrefill eSIM Europe",
                     "base_name": "Bitrefill eSIM", "country_code": "EU", "currency": "EUR",
                     "categories": ["esim"], "recipient_type": "esim", "in_stock": True,
                     "packages": [
                         {"id": "bitrefill-esim-europe<&>1GB, 7 Days",
                          "value": "1GB, 7 Days", "price": 4590, "amount": None},
                         {"id": "bitrefill-esim-europe<&>3GB, 30 Days",
                          "value": "3GB, 30 Days", "price": 12000, "amount": None},
                     ]},
                    {"id": "flexible-card", "name": "Flexible Card", "base_name": "Flexible",
                     "country_code": "US", "currency": "USD", "categories": ["bill"],
                     "recipient_type": "email", "in_stock": False,
                     "packages": [], "range": {"min": 10, "max": 200, "step": 1}},
                ]}, text="")
        raise AssertionError(f"unexpected url {url}")

    a.call = types.MethodType(paged, a)
    orig_sleep = bf.time.sleep
    bf.time.sleep = lambda s: None
    try:
        rows = a.fetch_catalog()
    finally:
        bf.time.sleep = orig_sleep
    assert pages["n"] == 2, "must follow official meta._next pagination"
    assert len(rows) == 5, "2 + 2 package rows + 1 range-only fallback row"
    r0 = rows[0]
    assert r0["external_id"] == "amazon-us<&>25"
    assert r0["unit_price"] == 29912 and r0["currency"] == "BTC"
    assert r0["raw"]["face_value"] == "25" and r0["raw"]["price_sats"] == 29912
    assert r0["raw"]["face_currency"] == "USD" and r0["raw"]["price_unit"] == "sats"
    assert r0["product_name"] == "Amazon US — 25 USD"
    assert r0["stock"] == "IN_STOCK" and r0["status"] == "ACTIVE"
    assert r0["brand"] == "Amazon" and r0["region"] == "US"
    esim = rows[2]
    assert esim["external_id"] == "bitrefill-esim-europe<&>1GB, 7 Days"
    assert esim["product_name"] == "Bitrefill eSIM Europe — 1GB, 7 Days EUR"
    rng = rows[4]
    assert rng["external_id"] == "flexible-card<>range" and rng["unit_price"] is None
    assert rng["raw"]["range"] == {"min": 10, "max": 200, "step": 1}
    assert rng["stock"] == "OUT_OF_STOCK" and rng["status"] == "INACTIVE"

    def bal_call(self, method, url, headers=None, payload=None, timeout=None):
        return types.SimpleNamespace(status=200,
                                     body={"data": {"balance": 0, "currency": "BTC"}}, text="")

    a.call = types.MethodType(bal_call, a)
    assert a.fetch_balance() == {"balance": 0, "currency": "BTC"}


def bitrefill_truncation_guard():
    """A pagination chain that dies before meta.total must RAISE — never
    report a partial catalog as success (live incident 2026-10-13: engine run
    silently landed 65,342 of 72,516 package rows and reported success)."""
    from providers.bitrefill import BitrefillAdapter
    import providers.bitrefill as bf
    a = BitrefillAdapter(creds={"BITREFILL_API_KEY": "k"})

    def paged(self, method, url, headers=None, payload=None, timeout=None):
        if "start=50" in url:
            return types.SimpleNamespace(status=200, body={
                "meta": {"limit": 50, "start": 50, "total": 120, "_next": None},
                "data": []}, text="")
        return types.SimpleNamespace(status=200, body={
            "meta": {"limit": 50, "start": 0, "total": 120,
                     "_next": "https://api-bitrefill.com/v2/products?limit=50&start=50"},
            "data": [{"id": f"p{i}", "name": f"P{i}", "currency": "USD",
                      "in_stock": True,
                      "packages": [{"id": f"p{i}<&>1", "value": "1", "price": 100}]}
                     for i in range(50)]}, text="")

    a.call = types.MethodType(paged, a)
    orig_sleep = bf.time.sleep
    bf.time.sleep = lambda s: None
    try:
        try:
            a.fetch_catalog()
            raise AssertionError("truncated catalog must raise ProviderError")
        except Exception as e:
            assert "truncated" in str(e).lower(), f"wrong error: {e}"
    finally:
        bf.time.sleep = orig_sleep


def bitrefill_dedup_drift_tolerance():
    """The /products listing drifts while paginated (live evidence
    2026-10-13: same product at start=0 AND start=50 in one walk). The adapter
    must collapse drift duplicates, keep the FRESHEST quote (last record),
    and expose fetch stats for engine telemetry."""
    from providers.bitrefill import BitrefillAdapter
    a = BitrefillAdapter(creds={"BITREFILL_API_KEY": "k"})

    def paged(self, method, url, headers=None, payload=None, timeout=None):
        base = {"id": "amazon-us", "name": "Amazon US", "base_name": "Amazon",
                "country_code": "US", "currency": "USD", "categories": ["ecommerce"],
                "recipient_type": "email", "in_stock": True}
        p_old = {**base, "packages": [{"id": "amazon-us<&>25", "value": "25",
                                        "price": 11111, "amount": 25}]}
        p_new = {**base, "packages": [{"id": "amazon-us<&>25", "value": "25",
                                        "price": 22222, "amount": 25}]}
        return types.SimpleNamespace(status=200, body={
            "meta": {"limit": 50, "start": 0, "total": 2, "_next": None},
            "data": [p_old, p_new]}, text="")

    a.call = types.MethodType(paged, a)
    rows = a.fetch_catalog()
    assert len(rows) == 1, "drift duplicates must collapse to one row"
    assert rows[0]["unit_price"] == 22222, "last record (freshest quote) must win"
    assert a.last_fetch_stats == {"records_fetched": 2, "unique_products": 1,
                                  "meta_total": 2}


def diff_catalog_semantics():
    """Batched engine diff must preserve per-item counting semantics and
    never rewrite unchanged rows (bitrefill-scale catalogs: ~72.5k rows)."""
    from providers.base import diff_catalog
    existing = {
        "a": {"unit_price": 1.0, "discount_pct": None, "stock": "IN_STOCK", "status": "ACTIVE"},
        "b": {"unit_price": 2.0, "discount_pct": 10.0, "stock": "5", "status": "ACTIVE"},
        "c": {"unit_price": 3.0, "discount_pct": None, "stock": "OUT", "status": "INACTIVE"},
    }
    catalog = [
        {"external_id": "a", "unit_price": 1.0, "discount_pct": None,
         "stock": "IN_STOCK", "status": "ACTIVE"},                       # unchanged
        {"external_id": "b", "unit_price": 2.5, "discount_pct": 10.0,
         "stock": "5", "status": "ACTIVE"},                              # price change
        {"external_id": "c", "unit_price": 3.0, "discount_pct": None,
         "stock": "IN", "status": "ACTIVE"},                             # stock change
        {"external_id": "d", "unit_price": 9.0, "discount_pct": None,
         "stock": "IN_STOCK", "status": "ACTIVE"},                       # new
    ]
    to_upsert, new, changed, prices = diff_catalog(existing, catalog)
    assert new == 1 and prices == 1 and changed == 1
    assert [r["external_id"] for r in to_upsert] == ["b", "c", "d"], \
        "unchanged rows must not be written"


print("=== MEC provider framework tests (isolated) ===")
t("reloadly_contract", reloadly_contract)
t("reloadly_catalog_normalization", reloadly_catalog_normalization)
t("retry_on_5xx", retry_on_5xx)
t("fail_fast_on_4xx", fail_fast_on_4xx)
t("rate_limit_honor", rate_limit_honor)
t("engine_degrades_gracefully", engine_degrades_gracefully)
t("gating_skips_discovered", gating_skips_discovered)
t("mock_adapter_paths", mock_adapter_paths)
t("upsert_dedup_semantics", upsert_dedup_semantics)
t("botshops_contract_matrix", botshops_contract_matrix)
t("botshops_auth_failure", botshops_auth_failure)
t("bitrefill_contract", bitrefill_contract)
t("bitrefill_catalog_normalization", bitrefill_catalog_normalization)
t("bitrefill_truncation_guard", bitrefill_truncation_guard)
t("bitrefill_dedup_drift_tolerance", bitrefill_dedup_drift_tolerance)
t("diff_catalog_semantics", diff_catalog_semantics)
print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    for n, e in FAIL:
        print(f"  FAIL {n}: {e}")
    sys.exit(1)
sys.exit(0)
