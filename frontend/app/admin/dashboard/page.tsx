"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getAdminAnalyticsSummary } from "@/lib/api-client";
import type { AdminAnalyticsSummary } from "@/lib/types";

export default function AdminDashboardPage() {
  const [data, setData] = useState<AdminAnalyticsSummary | null>(null);
  useEffect(() => { getAdminAnalyticsSummary().then(setData).catch(() => undefined); }, []);
  const cards = data ? [
    ["Users", data.total_users], ["Students", data.total_students], ["PG owners", data.total_pg_owners],
    ["Total PGs", data.total_pg_listings], ["Pending PGs", data.pending_pg_listings], ["Approved PGs", data.approved_pg_listings],
    ["Revenue", `Rs. ${data.total_credit_revenue_rupees}`], ["Credits sold", data.total_credits_purchased], ["Unlocks", data.total_contact_unlocks],
    ["Open reports", data.open_reports], ["Featured", data.active_featured_listings],
  ] : [];
  return (
    <ProtectedRoute roles={["admin", "super_admin"]}>
      <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-semibold tracking-normal">Admin dashboard</h1>
        <p className="mt-2 text-stone-600">Platform analytics, moderation, revenue, and verification health.</p>
        <div className="mt-8 grid gap-4 md:grid-cols-4">{cards.map(([label, value]) => <Card key={label}><CardHeader><CardTitle>{value}</CardTitle><CardDescription>{label}</CardDescription></CardHeader></Card>)}</div>
      </main>
    </ProtectedRoute>
  );
}
