import type { Metadata } from "next";

import { AuthProvider } from "@/components/auth/auth-provider";
import { Footer } from "@/components/layout/footer";
import { Navbar } from "@/components/layout/navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "CampusStay - Find Verified PGs Near LPU",
    template: "%s | CampusStay",
  },
  description: "Find verified PGs near LPU with real photos, prices, facilities, reviews, distance, and secure owner contact unlocks.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Navbar />
          {children}
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
