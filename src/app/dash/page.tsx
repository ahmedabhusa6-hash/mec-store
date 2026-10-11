import { redirect } from "next/navigation";
import { getOwner } from "@/lib/auth";
import { Dashboard } from "@/components/dashboard/shell";

export const dynamic = "force-dynamic";

export default async function DashPage() {
  const owner = await getOwner();
  if (!owner) redirect("/login");
  return <Dashboard />;
}
