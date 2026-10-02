import { getOrCreateWallet, walletBalance, credit, STORE_MODE } from "@/lib/engine";
import { normalizePhone, DEPOSIT_MIN, DEPOSIT_MAX, round2 } from "@/lib/format";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const limited = guard(req, "deposit");
  if (limited) return limited;

  let body: { phone?: string; amountUsd?: number };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "طلب غير صالح" }, { status: 400 });
  }

  const phone = normalizePhone(body.phone);
  const amount = Number(body.amountUsd);
  if (!phone) {
    return Response.json({ ok: false, error: "جوال صحيح مطلوب" }, { status: 400 });
  }
  if (!Number.isFinite(amount) || amount < DEPOSIT_MIN || amount > DEPOSIT_MAX) {
    return Response.json(
      { ok: false, error: `الإيداع بين $${DEPOSIT_MIN} و$${DEPOSIT_MAX} (حدود W1)` },
      { status: 400 }
    );
  }

  const wallet = await getOrCreateWallet(phone);

  if (STORE_MODE === "live") {
    // LIVE: generate a dedicated deposit address + wait for on-chain confirmation.
    // (Wire-up of real TRC-20 confirmation webhook is W2 scope; deposits stay manual-gated.)
    return Response.json({
      ok: true,
      pending: true,
      note: "الوضع الحي: سيُعرض عنوان إيداع مخصص — يُقيّد الرصيد بعد تأكيد on-chain (بلوك واحد)",
    });
  }

  // SANDBOX: instant marked demo credit
  const ref = `dep-${Date.now().toString(36)}`;
  await credit(wallet.id, "deposit", round2(amount), ref, "إيداع تجريبي (sandbox) — فوري");
  const balance = await walletBalance(wallet.id);
  return Response.json({
    ok: true, credited: round2(amount), balance,
    note: "إيداع تجريبي (sandbox) — فوري",
  });
}
