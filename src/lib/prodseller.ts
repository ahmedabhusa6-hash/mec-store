// ProdSeller API client — live wholesale supplier (psk_ key, bronze tier).
// Endpoints verified live 2026-09-27/28 (MEC-6/8): GET /v1/balance, GET /v1/products.

const BASE = process.env.PRODSELLER_API_URL || "https://prodseller.com/v1";
const KEY = process.env.PRODSELLER_API_KEY || "";

export type PsProduct = {
  id?: string | number;
  name?: string;
  price?: number;
  stock?: number | null;
  [k: string]: unknown;
};

export type PsBalance = {
  balance?: number;
  username?: string;
  membership?: string;
  [k: string]: unknown;
};

async function psGet<T>(path: string, timeoutMs = 20000): Promise<T> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: { "X-API-Key": KEY, Accept: "application/json" },
      signal: ctrl.signal,
      cache: "no-store",
    });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`ProdSeller ${path} HTTP ${res.status} ${body.slice(0, 120)}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

export async function psBalance(): Promise<PsBalance | null> {
  if (!KEY) return null;
  try {
    return await psGet<PsBalance>("/balance");
  } catch {
    return null;
  }
}

export async function psProducts(): Promise<PsProduct[] | null> {
  if (!KEY) return null;
  try {
    const data = await psGet<PsProduct[] | { products?: PsProduct[]; data?: PsProduct[] }>(
      "/products",
      25000
    );
    if (Array.isArray(data)) return data;
    if (Array.isArray((data as any)?.products)) return (data as any).products;
    if (Array.isArray((data as any)?.data)) return (data as any).data;
    return [];
  } catch {
    return null;
  }
}

/**
 * Real purchase (live mode only). Sandbox mode never calls this.
 * NOTE: purchase endpoint contract (POST /v1/orders) — used only when STORE_MODE=live.
 */
export async function psPurchase(productId: string, qty = 1): Promise<{ ok: boolean; payload?: string; error?: string }> {
  if (!KEY) return { ok: false, error: "no key" };
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 30000);
  try {
    const res = await fetch(`${BASE}/orders`, {
      method: "POST",
      headers: { "X-API-Key": KEY, "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: qty }),
      signal: ctrl.signal,
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) return { ok: false, error: `HTTP ${res.status}` };
    return { ok: true, payload: JSON.stringify(body) };
  } catch (e) {
    return { ok: false, error: String(e).slice(0, 120) };
  } finally {
    clearTimeout(t);
  }
}
