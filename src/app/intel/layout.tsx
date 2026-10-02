import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Supplier Intelligence — مركز استخبارات الأسعار",
  description:
    "لوحة المالك: استخبارات أسعار الموردين، فجوات API، دراسات المشروع، سلاسل التوريد — 17 تبويبًا بحثيًا كاملًا.",
  robots: { index: false, follow: false },
};

export default function IntelLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
