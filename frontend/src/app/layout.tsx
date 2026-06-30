import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { AuthProvider } from "@/providers/AuthProvider";

const inter = Inter({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GreenSprint",
  description: "Sustainability Intelligence Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      data-scroll-behavior="smooth"
    >
      <body
        className={`
          ${inter.className}
          bg-black
          text-white
        `}
      >
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}