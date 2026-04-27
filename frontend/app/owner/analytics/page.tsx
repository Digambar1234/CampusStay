"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { StatusBadge } from "@/components/pg/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getOwnerListingAnalytics } from "@/lib/api-client";
import type { OwnerListingAnalytics } from "@/lib/types";

export default function OwnerAnalyticsPage() {
  const [items, setItems] = useState<OwnerListingAnalytics[]>([]);
  useEffect(() => { getOwnerListingAnalytics().then(setItems).catch(() => setItems([])); }, []);
  return <ProtectedRoute roles={["pg_owner"]}><main className="mx-auto max-w-7xl px-4 py-12"><h1 className="text-3xl font-semibold">Listing analytics</h1><div className="mt-8 grid gap-4">{items.map((item) => <Card key={item.pg_id}><CardHeader className="flex flex-row justify-between"><CardTitle>{item.pg_name}</CardTitle><StatusBadge status={item.status} /></CardHeader><CardContent className="grid gap-2 text-sm md:grid-cols-5"><span>Views: {item.views_count}</span><span>Unlocks: {item.contact_unlock_count}</span><span>Reviews: {item.review_count}</span><span>Rating: {item.average_rating ?? "-"}</span><span>{item.is_featured ? "Featured" : "Not featured"}</span></CardContent></Card>)}</div></main></ProtectedRoute>;
}
