// MEC shared helpers — phone/region/price utilities
export const REGIONS = {
  SA: { label: "🇸🇦 السعودية — ر.س", currency: "SAR" },
  YE: { label: "🇾🇪 اليمن — $", currency: "USD" },
  WW: { label: "🌍 دولي — $", currency: "USD" },
} as const;

export type RegionCode = keyof typeof REGIONS;

/** Tight phone validation: +9665xxxxxxxx / +9677xxxxxxxx (8-9 digits after country code). */
export function normalizePhone(input: unknown): string | null {
  if (typeof input !== "string") return null;
  const cleaned = input.replace(/[^\d+]/g, "");
  if (!/^\+96[67]\d{8,9}$/.test(cleaned)) return null;
  return cleaned;
}

export function regionFromPhone(phone: string): RegionCode {
  const digits = phone.replace(/\D/g, "");
  if (digits.startsWith("966")) return "SA";
  if (digits.startsWith("967")) return "YE";
  return "WW";
}

export function maskPhone(phone: string): string {
  if (phone.length < 6) return phone;
  const cc = phone.slice(0, 4); // +966 / +967
  return `${cc}••••${phone.slice(-4)}`;
}

export function fmtPrice(price: number, currency: string): string {
  return currency === "SAR" ? `${round2(price)} ر.س` : `$${round2(price).toFixed(2)}`;
}

export function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

/** SAR↔USD peg 3.75 */
export function sarToUsd(sar: number): number {
  return round2(sar / 3.75);
}

const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // no confusing chars
export function genPublicId(): string {
  let s = "";
  for (let i = 0; i < 8; i++) s += ALPHABET[Math.floor(Math.random() * ALPHABET.length)];
  return `MEC-L${s}`;
}

export const STATUS_AR: Record<string, string> = {
  pending_payment: "بانتظار الدفع",
  paid: "تم الدفع — قيد التوجيه",
  routing: "الموجّه يشتري من المورد",
  delivered: "تم التسليم ✓",
  failed: "تعذّر التنفيذ — استُرد المبلغ",
};

// FIX (P3, AUDIT-2 D1): shared by engine.ts + orders route (was duplicated)
export const SUPPLIER_NAMES: Record<string, string> = {
  ps: "ProdSeller", sv: "StackVault", turgame: "Turgame", ggsel: "GGSel",
};

export const STEP_AR: Record<string, string> = {
  skipped_no_float: "تجاوز — حارس الرصيد",
  skipped_margin: "تجاوز — حارس الهامش",
  skipped_oos: "تجاوز — نفد المخزون",
  skipped_breaker: "تجاوز — قاطع الدائرة مفتوح",
  skipped_no_external_id: "تجاوز — معرّف المورد غير مضبوط",
  purchased: "شراء آلي ناجح",
  purchase_failed: "فشل الشراء",
  sandbox_purchase: "شراء محاكى (تجريبي)",
};

export const TX_AR: Record<string, string> = {
  deposit: "إيداع",
  purchase: "شراء",
  refund: "استرداد",
  cashback: "كاش باك",
  apology: "رصيد اعتذار",
};

export const RAILS = ["wallet", "trc20", "binance_pay"] as const;
export type Rail = (typeof RAILS)[number];

export const DEPOSIT_MIN = 5;
export const DEPOSIT_MAX = 500;
export const MARGIN_CAP = 0.9; // cost must be <= 90% of sale price
export const CASHBACK_RATE = 0.01;
export const APOLOGY_USD = 1;
export const SAR_PEG = 3.75;
