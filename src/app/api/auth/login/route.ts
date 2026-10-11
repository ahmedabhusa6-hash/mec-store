import { authenticate, createToken, SESSION_COOKIE, sessionCookieOptions } from "@/lib/auth";
import { guard, clientIp } from "@/lib/ratelimit";
import { audit, raiseAlert } from "@/lib/audit";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const limited = guard(req, "login");
  if (limited) return limited;

  let email = "";
  try {
    const body = (await req.json()) as { email?: string; password?: string };
    email = (body.email ?? "").trim().toLowerCase();
    const password = body.password ?? "";
    if (!email || !password) {
      return Response.json({ error: "البريد وكلمة المرور مطلوبان" }, { status: 400 });
    }
    const res = await authenticate(email, password);
    if (!res.ok) {
      await audit(email, "auth.login_failed", { ip: clientIp(req) });
      await raiseAlert("warning", "security", "محاولة دخول فاشلة", `بريد: ${email}`, "auth", email);
      return Response.json({ error: res.reason }, { status: 401 });
    }
    const token = createToken(res.session);
    await audit(email, "auth.login_ok", { ip: clientIp(req) });
    const resp = Response.json({ ok: true, email, role: res.session.role });
    resp.headers.append(
      "Set-Cookie",
      serializeCookie(SESSION_COOKIE, token, sessionCookieOptions()),
    );
    return resp;
  } catch (e) {
    return Response.json({ error: "طلب غير صالح" }, { status: 400 });
  }
}

function serializeCookie(name: string, value: string, opts: ReturnType<typeof sessionCookieOptions>): string {
  const parts = [`${name}=${value}`, `Path=${opts.path}`, `Max-Age=${opts.maxAge}`];
  if (opts.httpOnly) parts.push("HttpOnly");
  if (opts.secure) parts.push("Secure");
  parts.push(`SameSite=${opts.sameSite === "lax" ? "Lax" : opts.sameSite}`);
  return parts.join("; ");
}
