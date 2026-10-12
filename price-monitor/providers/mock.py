"""Mock adapter — isolated simulation for tests ONLY (master prompt §11:
no real orders; sandbox/read-only/mocked for testing). Never talks to a network.
Enabled only when provider row code='mock' exists (created by the test suite;
not part of the production registry)."""
import uuid


class MockAdapter:
    code = "mock"

    def __init__(self, creds=None):
        self.creds = creds or {}

    def credentials_present(self):
        return bool(self.creds.get("MOCK_KEY"))

    def authenticate(self):
        if self.creds.get("MOCK_KEY") == "fail-auth":
            raise RuntimeError("simulated auth failure")
        return True

    def fetch_catalog(self):
        if self.creds.get("MOCK_KEY") == "fail-catalog":
            raise RuntimeError("simulated catalog failure")
        n = int(self.creds.get("MOCK_SIZE", "3"))
        return [{
            "external_id": f"MOCK-{i}",
            "product_name": f"Mock Product {i}",
            "brand": "MockBrand",
            "region": "MOCK",
            "currency": "USD",
            "unit_price": 10.0 + i,
            "discount_pct": 5.0,
            "unit_cost": None,
            "stock": "IN_STOCK",
            "status": "ACTIVE",
            "raw": {"mock": True},
        } for i in range(n)]

    def fetch_balance(self):
        return {"balance": 100.0, "currency": "USD"}
