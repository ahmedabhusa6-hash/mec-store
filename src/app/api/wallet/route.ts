import { db } from "@/lib/db";
import { walletBalance, walletTxs } from "@/lib/engine";
import { normalizePhone } from "@/lib/format";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * FIX (P1 regression, MEC-21-C R-2): this endpoint previously called
 * getOrCreateWallet() — silently CREATING wallet rows for arbitrary phones
 * (row-creation + registered-or-not oracle) and returning tx refs that leak
 * order publicIds (recon chain toward order detail). Now:
 * - read-only lookup (no row creation; wallet rows are born only from real
 *   user actions: deposit / checkout / confirm)
 * - unknown phone returns the SAME shape as a fresh empty wallet (no oracle)
 * - tx refs are stripped (recon reduction; UI never rendered them anyway)
 * Residual (documented): phone-as-bearer identity model remains until OTP (W2).
 */
export async function GET(req: Request) {
  const limited = guard(req, "wallet_read");
  if (limited) return limited;

  const url = new URL(req.url);
  const phone = normalizePhone(url.searchParams.get("phone"));
  if (!phone) {
    return Response.json({ ok: false, error: "جوال صحيح مطلوب (+966/+967)" }, { status: 400 });
  }

  const wallet = await db.wallet.findUnique({ where: { phone }, select: { id: true } });
  if (!wallet) {
    return Response.json({ ok: true, balance: 0, txs: [] });
  }
  const [balance, txs] = await Promise.all([walletBalance(wallet.id), walletTxs(wallet.id)]);
  return Response.json({ ok: true, balance, txs });
}
