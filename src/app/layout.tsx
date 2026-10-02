import type { Metadata } from "next";
import { Tajawal, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

// FIX (MEC-21-B): production URL had no metadataBase — relative og:image/url and
// canonical tags cannot resolve without it. Env-overridable for future custom domain.
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://mec-store-production.up.railway.app";

// FIX (UX): Arabic-first product now uses a proper Arabic typeface (Tajawal —
// the de-facto standard for Saudi e-commerce) instead of Latin-only Geist
// with OS-dependent Arabic fallback. Numbers/code keep Geist Mono (LTR).
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
  metadataBase: new URL(SITE_URL),
  title: "متجر MEC الرقمي — اشتراكات AI وبث MENA بأسعار موثقة",
  description:
    "متجر منتجات رقمية: اشتراكات AI/SaaS، بث MENA (شاهد، أنغامي)، بطاقات إقليمية — شراء مباشر برقم الجوال، تسليم خلال دقائق، دفع USDT TRC-20 و Binance Pay.",
  keywords: [
    "اشتراكات رقمية",
    "شاهد VIP",
    "انغامي",
    "ChatGPT",
    "Gemini",
    "CapCut",
    "Canva",
    "Office 365",
    "بطاقات Steam",
    "USDT",
    "متجر رقمي",
  ],
  authors: [{ name: "MEC Digital Store" }],
  alternates: { canonical: "/" },
  robots: { index: true, follow: true },
  icons: {
    icon: [
      { url: "/logo.svg", type: "image/svg+xml" },
      { url: "/icon.png", type: "image/png", sizes: "512x512" },
    ],
    apple: "/apple-icon.png",
  },
  openGraph: {
    title: "متجر MEC الرقمي — تسليم فوري",
    description: "اشتراكات AI · بث MENA · بطاقات إقليمية بأفضل الأسعار الموثقة",
    siteName: "MEC Digital Store",
    type: "website",
    url: "/",
    locale: "ar_SA",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "متجر MEC الرقمي — اشتراكات AI وبث MENA بتسليم فوري",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "متجر MEC الرقمي — تسليم فوري",
    description: "اشتراكات AI · بث MENA · بطاقات إقليمية بأفضل الأسعار الموثقة",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" suppressHydrationWarning>
      <body
        className={`${tajawal.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
        style={{ fontFamily: "var(--font-tajawal), 'Segoe UI', Tahoma, Arial, sans-serif" }}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
