"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAdminRevenueAnalytics, getAdminTopPGs } from "@/lib/api-client";
import type { AdminRevenue, TopPG } from "@/lib/types";

export default function AdminAnalyticsPage() {
  const [revenue, setRevenue] = useState<AdminRevenue | null>(null);
  const [top, setTop] = useState<TopPG[]>([]);
  useEffect(() => { getAdminRevenueAnalytics().then(setRevenue); getAdminTopPGs().then(setTop); }, []);
  return <ProtectedRoute roles={["admin","super_admin"]}><main className="mx-auto max-w-7xl px-4 py-12"><h1 className="text-3xl font-semibold">Analytics</h1><div className="mt-8 grid gap-4 md:grid-cols-2"><Card><CardHeader><CardTitle>Revenue</CardTitle></CardHeader><CardContent><p>Rs. {revenue?.total_revenue_rupees ?? 0}</p><p>{revenue?.credits_sold ?? 0} credits sold</p></CardContent></Card><Card><CardHeader><CardTitle>Top PGs</CardTitle></CardHeader><CardContent className="grid gap-2">{top.map((pg) => <div key={pg.pg_id} className="rounded-md border p-3 text-sm">{pg.pg_name}: {pg.views} views, {pg.unlocks} unlocks, rating {pg.average_rating ?? "-"}</div>)}</CardContent></Card></div></main></ProtectedRoute>;
}
