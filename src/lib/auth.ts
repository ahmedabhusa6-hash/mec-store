/**
 * MEC — owner authentication (rebuild v4, 2026-10-11).
 * scrypt password hashing (node:crypto) + HMAC-SHA256 signed session cookie.
 * Single-owner model with lazy bootstrap from OWNER_EMAIL/OWNER_PASSWORD env
 * (env credentials always work as the master recovery path — changing the env
 * changes the password; the stored hash is kept in sync automatically).
 */
import { createHmac, randomBytes, scryptSync, timingSafeEqual } from "crypto";
import { cookies } from "next/headers";
import { sbGet, sbPatch, sbPost } from "./supabase";

export const SESSION_COOKIE = "mec_session";
const SESSION_TTL_S = 60 * 60 * 24 * 14; // 14 days

export type OwnerSession = { email: string; role: string; exp: number };

function secret(): string {
  const s = process.env.SESSION_SECRET;
  if (!s || s.length < 16) throw new Error("SESSION_SECRET not configured");
  return s;
}

// ─── passwords ────────────────────────────────────────────────────────
export function hashPassword(pw: string): string {
  const salt = randomBytes(16).toString("hex");
  const hash = scryptSync(pw, salt, 32).toString("hex");
  return `scrypt$${salt}$${hash}`;
}

export function verifyPassword(pw: string, stored: string): boolean {
  const parts = stored.split("$");
  if (parts.length !== 3 || parts[0] !== "scrypt") return false;
  const hash = scryptSync(pw, parts[1], 32);
  const expect = Buffer.from(parts[2], "hex");
  return hash.length === expect.length && timingSafeEqual(hash, expect);
}

// ─── signed session token ─────────────────────────────────────────────
function b64u(b: Buffer): string {
  return b.toString("base64url");
}

export function createToken(payload: OwnerSession): string {
  const body = b64u(Buffer.from(JSON.stringify(payload)));
  const sig = createHmac("sha256", secret()).update(body).digest("base64url");
  return `${body}.${sig}`;
}

export function verifyToken(token: string | undefined | null): OwnerSession | null {
  if (!token) return null;
  const [body, sig] = token.split(".");
  if (!body || !sig) return null;
  const expect = createHmac("sha256", secret()).update(body).digest();
  let got: Buffer;
  try {
    got = Buffer.from(sig, "base64url");
  } catch {
    return null;
  }
  if (got.length !== expect.length || !timingSafeEqual(got, expect)) return null;
  try {
    const payload = JSON.parse(Buffer.from(body, "base64url").toString()) as OwnerSession;
    if (!payload?.email || payload.exp < Math.floor(Date.now() / 1000)) return null;
    return payload;
  } catch {
    return null;
  }
}

// ─── cookie helpers (server components + route handlers) ──────────────
export async function getOwner(): Promise<OwnerSession | null> {
  const jar = await cookies();
  return verifyToken(jar.get(SESSION_COOKIE)?.value);
}

export function sessionCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: SESSION_TTL_S,
  };
}

// ─── users store (app_users table via REST) ──────────────────────────
type AppUserRow = { id: number; email: string; password_hash: string; role: string; last_login_at: string | null };

export async function findUser(email: string): Promise<AppUserRow | null> {
  const rows = await sbGet<AppUserRow[]>(
    `app_users?email=eq.${encodeURIComponent(email)}&select=id,email,password_hash,role,last_login_at`,
    5_000,
  );
  return rows?.[0] ?? null;
}

export async function upsertUser(email: string, passwordHash: string): Promise<void> {
  await sbPost(
    "app_users?on_conflict=email",
    { email, password_hash: passwordHash, role: "owner" },
    "resolution=merge-duplicates,return=minimal",
  );
}

export async function touchLogin(email: string): Promise<void> {
  await sbPatch(`app_users?email=eq.${encodeURIComponent(email)}`, {
    last_login_at: new Date().toISOString(),
  });
}

/** Full login logic: env master credentials + db user, with auto-bootstrap. */
export async function authenticate(
  email: string,
  password: string,
): Promise<{ ok: true; session: OwnerSession } | { ok: false; reason: string }> {
  const envEmail = process.env.OWNER_EMAIL ?? "";
  const envPw = process.env.OWNER_PASSWORD ?? "";
  const isMaster = envEmail && email === envEmail && envPw && password === envPw;

  let user: AppUserRow | null = null;
  try {
    user = await findUser(email);
  } catch {
    // app_users unreachable → fall back to env master only
  }

  if (isMaster) {
    // keep stored hash in sync with env master password
    try {
      await upsertUser(email, hashPassword(password));
    } catch { /* non-fatal */ }
  } else if (user && verifyPassword(password, user.password_hash)) {
    // regular db login
  } else {
    return { ok: false, reason: "بيانات الدخول غير صحيحة" };
  }

  try {
    await touchLogin(email);
  } catch { /* non-fatal */ }

  return {
    ok: true,
    session: {
      email,
      role: user?.role ?? "owner",
      exp: Math.floor(Date.now() / 1000) + SESSION_TTL_S,
    },
  };
}

/** Guard for admin API routes: returns session or a 401 Response. */
export async function requireOwner(): Promise<{ owner: OwnerSession } | { deny: Response }> {
  const owner = await getOwner();
  if (!owner) {
    return {
      deny: Response.json({ error: "غير مصرح — يتطلب تسجيل دخول المالك" }, { status: 401 }),
    };
  }
  return { owner };
}
