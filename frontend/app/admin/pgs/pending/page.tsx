"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/auth/auth-provider";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { EmptyState, ErrorState, LoadingState, rentRange } from "@/components/pg/state";
import { StatusBadge } from "@/components/pg/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getAdminPGs } from "@/lib/api-client";
import type { PGListing } from "@/lib/types";

export default function PendingPGsPage() {
  const [items, setItems] = useState<PGListing[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isLoading: authLoading } = useAuth();

  async function load() {
    setError(null);
    setIsLoading(true);
    try {
      const data = await getAdminPGs("pending");
      setItems(data.items);
    } catch (err) {
      setItems([]);
      setError(err instanceof Error ? err.message : "Could not load pending PGs.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (!authLoading && user && ["admin", "super_admin"].includes(user.role)) {
      load();
    } else if (!authLoading) {
      setIsLoading(false);
    }
  }, [authLoading, user?.id, user?.role]);

  return <AdminList title="Pending PGs" description="Review owner submissions before they go public." items={items} isLoading={isLoading} error={error} onRefresh={load} />;
}

export function AdminList({ title, description, items, isLoading, error, onRefresh }: { title: string; description: string; items: PGListing[]; isLoading?: boolean; error?: string | null; onRefresh?: () => void }) {
  return (
    <ProtectedRoute roles={["admin", "super_admin"]}>
      <main className="mx-auto max-w-7xl px-4 py-12">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
          <div><h1 className="text-3xl font-semibold">{title}</h1><p className="mt-2 text-stone-600">{description}</p></div>
          {onRefresh ? <Button type="button" variant="secondary" onClick={onRefresh}>Refresh</Button> : null}
        </div>
        {isLoading ? <div className="mt-8"><LoadingState /></div> : null}
        {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}
        {!isLoading && !error && items.length === 0 ? <div className="mt-8"><EmptyState title={`No ${title.toLowerCase()} found`} description="New owner submissions appear here after the owner clicks Submit for Review." /></div> : null}
        <div className="mt-8 grid gap-4">{!isLoading && !error ? items.map((pg) => (
          <Card key={pg.id}><CardHeader className="flex flex-col justify-between gap-3 md:flex-row md:items-start"><div><CardTitle>{pg.pg_name}</CardTitle><CardDescription>{pg.address}</CardDescription></div><StatusBadge status={pg.status} /></CardHeader><CardContent className="flex flex-col justify-between gap-4 md:flex-row md:items-center"><div className="grid gap-1 text-sm text-stone-600 md:grid-cols-6 md:gap-5"><span>{pg.owner?.full_name}</span><span>{pg.owner?.email}</span><span>{pg.owner?.phone}</span><span>{rentRange(pg.monthly_rent_min, pg.monthly_rent_max)}</span><span>{pg.distance_from_lpu_km ?? "-"} km</span><span>{pg.photos.length} photos / {pg.rooms.length} rooms</span></div><Button asChild><Link href={`/admin/pgs/${pg.id}`}>View details</Link></Button></CardContent></Card>
        )) : null}</div>
      </main>
    </ProtectedRoute>
  );
}
