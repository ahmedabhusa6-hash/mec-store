import { redirect } from "next/navigation";
import { getOwner } from "@/lib/auth";
import { LoginForm } from "@/components/dashboard/login-form";

export const dynamic = "force-dynamic";

export default async function LoginPage() {
  const owner = await getOwner();
  if (owner) redirect("/dash");
  return <LoginForm />;
}
