import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dark Pattern Auditor — AI-Powered Legal Compliance Scanner",
  description:
    "Automatically detect dark patterns using Playwright browser automation and classify them against live FTC and EU statutes.",
  openGraph: {
    title: "Dark Pattern Auditor",
    description: "AI-powered legal compliance scanner for dark patterns",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
      </head>
      <body className="min-h-screen bg-[#08090c] text-slate-200 antialiased">
        {children}
      </body>
    </html>
  );
}
