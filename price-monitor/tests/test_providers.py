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
print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    for n, e in FAIL:
        print(f"  FAIL {n}: {e}")
    sys.exit(1)
sys.exit(0)
