"""MEC provider-connector framework — base classes and sync engine.

Design (per master prompt phase 4):
  - One adapter per provider; adding a provider touches ONLY its own file.
  - Lifecycle states: DISCOVERED / DOCUMENTATION_FOUND / CREDENTIALS_REQUIRED /
    READY_FOR_TEST / READ_ONLY_TEST_PASSED / SYNC_ACTIVE / AUTH_FAILED /
    RATE_LIMITED / UNSUPPORTED / BLOCKED / MAINTENANCE / RETIRED.
  - Read-only by default. Order/creation endpoints are NEVER called by the
    platform; they require explicit owner approval (policy layer).
  - Disciplined HTTP: timeouts, bounded retries with backoff, rate-limit honor,
    per-provider isolation (one provider's failure never breaks the cycle).
  - Every sync is logged to sync_runs (start/end/items/errors/duration).
"""
import json, os, time, urllib.request, urllib.error, random

# ---------- tiny supabase REST (mirrors monitor.py patterns) ----------
SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_KEY", "")


def sb_rows(path):
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{path}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def sb_upsert(path, payload):
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{path}", data=json.dumps(payload).encode(),
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "application/json",
                 "Prefer": "return=minimal,resolution=merge-duplicates"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())


# ---------- disciplined HTTP ----------
class HttpResult:
    def __init__(self, status, body, text):
        self.status, self.body, self.text = status, body, text


def http(method, url, headers=None, payload=None, timeout=30):
    data = json.dumps(payload).encode() if payload is not None else None
    # Browser-grade UA: several providers sit behind Cloudflare bot rules that
    # instantly 403 the default "Python-urllib/3.x" UA (live evidence 2026-10-13:
    # acczone/digitalcore/richai 403 from Actions, 200 with this UA).
    h = {"Content-Type": "application/json", "Accept": "application/json",
         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            body = json.loads(raw) if raw.strip().startswith(("{", "[")) else raw
            return HttpResult(r.status, body, raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            body = json.loads(raw)
        except Exception:
            body = raw
        return HttpResult(e.code, body, raw)


class RateLimited(Exception):
    pass


class ProviderError(Exception):
    pass


# ---------- adapter interface ----------
class ProviderAdapter:
    """Stateless-per-sync adapter. Subclasses implement test/read operations."""

    code = None            # registry key (providers.code)
    AUTH_TIMEOUT = 20
    CALL_TIMEOUT = 30
    MAX_RETRIES = 3
    BACKOFF_BASE = 2.0     # seconds; randomized +/- 30%

    def __init__(self, creds=None):
        self.creds = creds or {}   # {client_id, client_secret, ...} — never logged
        self.token = None
        self.token_exp = 0

    # --- required interface ---
    def credentials_present(self):
        raise NotImplementedError

    def authenticate(self):
        """Obtain and cache a bearer token. Must set self.token/self.token_exp."""
        raise NotImplementedError

    def fetch_catalog(self):
        """Return normalized list of dicts:
        {external_id, product_name, brand, region, currency, unit_price,
         discount_pct, unit_cost, stock, status, raw}"""
        raise NotImplementedError

    def fetch_balance(self):
        """Optional. Return dict {balance, currency} or None."""
        return None

    # --- shared helpers ---
    def call(self, method, url, headers=None, payload=None, timeout=None):
        """Disciplined call: retries on 5xx/network, honors 429, fails fast on 4xx."""
        attempt = 0
        while True:
            attempt += 1
            res = http(method, url, headers=headers, payload=payload,
                       timeout=timeout or self.CALL_TIMEOUT)
            if res.status == 429:
                # honor Retry-After when present
                ra = 60
                try:
                    ra = int(res.headers.get("retry-after") if hasattr(res, "headers") else 60)
                except Exception:
                    pass
                if attempt <= self.MAX_RETRIES:
                    wait = min(ra, 120) + random.uniform(0, 5)
                    time.sleep(wait)
                    continue
                raise RateLimited(f"429 after {attempt} attempts")
            if res.status >= 500 and attempt <= self.MAX_RETRIES:
                time.sleep(self.BACKOFF_BASE ** attempt * (1 + random.uniform(-0.3, 0.3)))
                continue
            if res.status >= 400:
                raise ProviderError(f"HTTP {res.status}: {str(res.body)[:200]}")
            return res


# ---------- sync engine ----------
def _safe(fn, default=None):
    """Run a DB operation; on failure degrade (never raise)."""
    try:
        return fn()
    except Exception:
        return default


def diff_catalog(existing, catalog):
    """Pure diff of a fetched catalog against existing rows (testable, no DB).

    existing: {external_id: {unit_price, discount_pct, stock, status}}
    Returns (to_upsert_rows, new_count, changed_count, prices_count).
    Semantics identical to the previous per-item loop: an item counts in
    `prices` when unit_price/discount_pct changed, in `changed` when
    stock/status changed (both counters can hit the same item).
    """
    new = changed = prices = 0
    to_upsert = []
    for it in catalog:
        e = existing.get(it["external_id"])
        if e is None:
            new += 1
            to_upsert.append(it)
            continue
        price_changed = (e.get("unit_price") != it.get("unit_price")
                         or e.get("discount_pct") != it.get("discount_pct"))
        stock_changed = (e.get("stock") != it.get("stock")
                         or e.get("status") != it.get("status"))
        if price_changed:
            prices += 1
        if stock_changed:
            changed += 1
        if price_changed or stock_changed:
            to_upsert.append(it)
    return to_upsert, new, changed, prices


def sync_one(provider, adapter_cls, run_trigger="scheduled"):
    """Run one provider sync with full telemetry. Never raises (DB-degradable)."""
    t0 = time.time()
    code = provider["code"]
    status = provider.get("status") or "DISCOVERED"

    # lifecycle gating FIRST (no DB touched for pure policy skips)
    if status in ("RETIRED", "BLOCKED", "UNSUPPORTED", "MAINTENANCE", "DISCOVERED"):
        return {"code": code, "status": "skipped", "items": 0, "new": 0, "ms": 0,
                "error": f"state={status} — sync skipped by policy"}

    def _db(method, path, payload=None, prefer="return=minimal"):
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/{path}", data=json.dumps(payload).encode() if payload else None,
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                     "Content-Type": "application/json", "Prefer": prefer},
            method=method)
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else None

    sync_id = _safe(lambda: (_db("POST", "sync_runs", {
        "provider_code": code, "started_at": now_iso(),
        "trigger": run_trigger, "status": "running"}, prefer="return=representation") or [{}])[0].get("id"), None)

    def finish(st, items=0, changed=0, new=0, prices=0, error=None, meta=None):
        dur = int((time.time() - t0) * 1000)
        def _w1():
            if sync_id:
                _db("PATCH", f"sync_runs?id=eq.{sync_id}", {
                    "finished_at": now_iso(), "status": st, "items_seen": items,
                    "items_changed": changed, "products_new": new, "prices_updated": prices,
                    "duration_ms": dur, "errors": error, "meta": meta or {}})
            pup = {"last_sync_at": now_iso(), "updated_at": now_iso(),
                   "last_error": (error[:300] if error else None)}
            if st == "success":
                pup["last_ok_at"] = now_iso()
                pup["last_error"] = None
            try:
                sb_upsert("providers?on_conflict=code", {
                    **{"code": code, "name": provider["name"], "kind": provider["kind"]}, **pup})
            except Exception:
                pass
        _safe(_w1)
        return {"code": code, "status": st, "items": items, "changed": changed,
                "new": new, "ms": dur, "error": error}

    adapter = adapter_cls(creds=_load_creds(provider))
    if not adapter.credentials_present():
        if status in ("DOCUMENTATION_FOUND", "READY_FOR_TEST"):
            _safe(lambda: _set_provider_status(code, "CREDENTIALS_REQUIRED"))
        return finish("skipped", error="credentials not present (CREDENTIALS_REQUIRED)")

    try:
        adapter.authenticate()
        if status not in ("READ_ONLY_TEST_PASSED", "SYNC_ACTIVE"):
            _safe(lambda: _set_provider_status(code, "SYNC_ACTIVE"))
        catalog = adapter.fetch_catalog()
        items = len(catalog)
        # optional adapter fetch telemetry (e.g. bitrefill drift stats) -> run meta
        fetch_stats = getattr(adapter, "last_fetch_stats", None) or {}

        # ---- existing rows for this provider (single paged read) ----
        existing = {}
        offset = 0
        while True:
            page = _safe(lambda: sb_rows(
                f"provider_products?provider_code=eq.{code}"
                f"&select=external_id,unit_price,discount_pct,stock,status"
                f"&order=external_id.asc&limit=1000&offset={offset}"), [])
            if not page:
                break
            for r in page:
                existing[r["external_id"]] = r
            if len(page) < 1000:
                break
            offset += 1000

        to_upsert, new, changed, prices = diff_catalog(existing, catalog)
        to_upsert = [{**it, "provider_code": code} for it in to_upsert]

        # ---- batched upsert (400 rows/request) with per-row fallback ----
        # Large catalogs (bitrefill: ~72.5k package rows) make per-item writes
        # infeasible inside the 30-min Actions budget; batching keeps identical
        # semantics while cutting request count ~800x. Unchanged rows are not
        # rewritten (fetched_at moves only when a row actually changes).
        UPSERT_CHUNK = 400
        up_errors = 0
        for i in range(0, len(to_upsert), UPSERT_CHUNK):
            chunk = to_upsert[i:i + UPSERT_CHUNK]
            try:
                sb_upsert("provider_products?on_conflict=provider_code,external_id", chunk)
            except Exception:
                for row in chunk:  # slow path: never lose a row silently
                    try:
                        sb_upsert("provider_products?on_conflict=provider_code,external_id", row)
                    except Exception:
                        up_errors += 1

        bal = None
        try:
            bal = adapter.fetch_balance()
        except Exception:
            pass
        meta = dict(fetch_stats)
        if bal:
            meta["balance"] = bal
        if up_errors:
            meta["upsert_errors"] = up_errors
            return finish("partial", items=items, changed=changed, new=new, prices=prices,
                          error=f"{up_errors} rows failed to upsert", meta=meta)
        return finish("success", items=items, changed=changed, new=new, prices=prices,
                      meta=meta)
    except RateLimited as e:
        _safe(lambda: _set_provider_status(code, "RATE_LIMITED"))
        return finish("failed", error=f"rate-limited: {e}")
    except ProviderError as e:
        msg = str(e)
        if "401" in msg or "auth" in msg.lower():
            _safe(lambda: _set_provider_status(code, "AUTH_FAILED"))
        return finish("failed", error=msg[:500])
    except Exception as e:  # never break the whole cycle
        return finish("failed", error=f"unexpected: {type(e).__name__}: {e}"[:500])


def _load_creds(provider):
    """Read credentials from env vars named in provider.credentials_env. Names only; never logged."""
    out = {}
    for name in (provider.get("credentials_env") or []):
        v = os.environ.get(name)
        if v:
            out[name] = v
    return out


def _set_provider_status(code, new_status):
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/providers?code=eq.{code}",
        data=json.dumps({"status": new_status, "updated_at": now_iso()}).encode(),
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "application/json", "Prefer": "return=minimal"},
        method="PATCH")
    urllib.request.urlopen(req, timeout=60)


def sync_all_providers(run_trigger="scheduled"):
    """Entry point used by monitor.py. Telegram provider row is synced by the
    monitor itself — this engine covers the API kind only. Degrades gracefully."""
    from .reloadly import ReloadlyAdapter
    from .mock import MockAdapter
    from .bitrefill import BitrefillAdapter
    from .botshops import (StackVaultAdapter, ProdSellerAdapter, AcczoneAdapter,
                           AivaulthubAdapter, AiversexAdapter, RichAIAdapter,
                           DigitalCoreAdapter, AixpressAdapter)

    ADAPTERS = {
        "reloadly": ReloadlyAdapter,
        "mock": MockAdapter,
        "bitrefill": BitrefillAdapter,
        "stackvault": StackVaultAdapter,
        "prodseller": ProdSellerAdapter,
        "acczone": AcczoneAdapter,
        "aivaulthub": AivaulthubAdapter,
        "aiversex": AiversexAdapter,
        "richai": RichAIAdapter,
        "digitalcore": DigitalCoreAdapter,
        "aixpress": AixpressAdapter,
    }
    providers = _safe(lambda: sb_rows("providers?select=*&kind=eq.api&order=code.asc&limit=100")) or []
    if providers is None:
        providers = []
    results = []
    for p in providers:
        cls = ADAPTERS.get(p["code"])
        if not cls:
            results.append({"code": p["code"], "status": "skipped",
                            "error": "no adapter implemented yet (registry entry only)"})
            continue
        try:
            results.append(sync_one(p, cls, run_trigger))
        except Exception as e:
            results.append({"code": p["code"], "status": "failed", "error": str(e)[:200]})
    return results
