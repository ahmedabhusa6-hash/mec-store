// Quick DB connectivity probe — prints error class/message only, never credentials
import { PrismaClient } from "@prisma/client";
const url = process.env.DATABASE_URL || "";
const masked = url.replace(/:[^:@/]*@/, ":****@");
console.log("DATABASE_URL (masked):", masked.slice(0, 90) + "...");
const db = new PrismaClient({ log: ["error"] });
try {
  const n = await db.product.count();
  console.log("SUCCESS — product count:", n);
} catch (e) {
  const err = e;
  console.error("PRISMA ERROR:", err.constructor.name, "-", String(err.message).slice(0, 500));
} finally {
  await db.$disconnect();
}
