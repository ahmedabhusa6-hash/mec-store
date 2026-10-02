// MEC admin auth — FIX for audit P0 finding: /api/admin/* was fully public.
// Both /api/admin/stats and /api/admin/sync leaked supplier account data and
// allowed anonymous 25s live syncs. Now requires x-admin-token == env ADMIN_TOKEN.

export function isAdmin(req: Request): boolean {
  const expected = process.env.ADMIN_TOKEN;
  if (!expected || expected.length < 16) {
    // If ADMIN_TOKEN unset/too-weak → deny everything (fail-closed).
    return false;
  }
  const provided =
    req.headers.get("x-admin-token") ||
    req.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ||
    "";
  return timingSafeEqual(provided, expected);
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export function unauthorized(): Response {
  return Response.json(
    { ok: false, error: "غير مصرح — لوحة التشغيل تتطلب مفتاح تشغيل صحيحًا" },
    { status: 401, headers: { "WWW-Authenticate": "Bearer" } }
  );
}
