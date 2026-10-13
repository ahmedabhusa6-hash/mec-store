import type { Metadata } from "next";
import { Tajawal, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const tajawal = Tajawal({
  variable: "--font-tajawal",
  subsets: ["arabic", "latin"],
  weight: ["400", "500", "700", "800"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ميزان MizanIQ — استخبارات أسعار الموردين الحية",
  description:
    "ميزان (MizanIQ): رصد آلي مستمر لأسعار المنتجات الرقمية من قنوات الموردين في تلغرام وواجهات API الرسمية — كل سعر بمصدره وتاريخه. قرار شراء أذكى من بيانات أصدق.",
  authors: [{ name: "MizanIQ — ميزان" }],
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" suppressHydrationWarning>
      <body
        className={`${tajawal.variable} ${geistMono.variable} antialiased bg-zinc-950 text-zinc-100`}
        style={{ fontFamily: "var(--font-tajawal), 'Segoe UI', Tahoma, Arial, sans-serif" }}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
