"use client";

import Link from "next/link";
import { PlusCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getOwnerListings } from "@/lib/api-client";
import { getOwnerAnalyticsSummary } from "@/lib/api-client";
import type { PGListingSummary } from "@/lib/types";

export default function OwnerDashboardPage() {
  const [items, setItems] = useState<PGListingSummary[]>([]);
  const [analytics, setAnalytics] = useState<{ total_views: number; total_contact_unlocks: number; total_reviews: number; average_rating_across_listings: number | null } | null>(null);

  useEffect(() => {
    getOwnerListings().then((data) => setItems(data.items)).catch(() => setItems([]));
    getOwnerAnalyticsSummary().then(setAnalytics).catch(() => undefined);
  }, []);

  const counts = useMemo(() => ({
    total: items.length,
    draft: items.filter((item) => item.status === "draft").length,
    pending: items.filter((item) => item.status === "pending_review").length,
    approved: items.filter((item) => item.status === "approved").length,
    rejected: items.filter((item) => item.status === "rejected").length,
  }), [items]);

  return (
    <ProtectedRoute roles={["pg_owner"]}>
      <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="text-3xl font-semibold tracking-normal">Owner dashboard</h1>
            <p className="mt-2 text-stone-600">Track listing status and submit verified PG inventory for review.</p>
          </div>
          <Button asChild><Link href="/owner/listings/new"><PlusCircle className="h-4 w-4" /> Add New PG</Link></Button>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-6">
          {[
            ["Total listings", counts.total],
            ["Draft", counts.draft],
            ["Pending review", counts.pending],
            ["Approved", counts.approved],
            ["Rejected", counts.rejected],
            ["Views", analytics?.total_views ?? 0],
            ["Unlocks", analytics?.total_contact_unlocks ?? 0],
            ["Reviews", analytics?.total_reviews ?? 0],
            ["Avg rating", analytics?.average_rating_across_listings ?? "-"],
          ].map(([label, value]) => (
            <Card key={label}><CardHeader><CardTitle>{value}</CardTitle><CardDescription>{label}</CardDescription></CardHeader></Card>
          ))}
        </div>
      </main>
    </ProtectedRoute>
  );
}
