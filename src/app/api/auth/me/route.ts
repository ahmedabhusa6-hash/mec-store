import { getOwner } from "@/lib/auth";

export const dynamic = "force-dynamic";

export async function GET() {
  const owner = await getOwner();
  if (!owner) return Response.json({ authenticated: false }, { status: 401 });
  return Response.json({ authenticated: true, email: owner.email, role: owner.role });
}
