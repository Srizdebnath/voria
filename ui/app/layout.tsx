import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Voria - AI-Powered Bug Fixing Tool",
  description: "Voria is an AI-powered CLI tool that automatically fixes bugs and implements features in your codebase.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}