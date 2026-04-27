"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { EmptyState, ErrorState, rentRange } from "@/components/pg/state";
import { StatusBadge } from "@/components/pg/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { deleteOwnerListing, getOwnerListings, submitOwnerListing } from "@/lib/api-client";
import type { PGListingSummary } from "@/lib/types";

export default function OwnerListingsPage() {
  const [items, setItems] = useState<PGListingSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const data = await getOwnerListings();
      setItems(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load listings.");
    }
  }

  useEffect(() => { load(); }, []);

  async function submit(id: string) {
    setError(null);
    try { await submitOwnerListing(id); await load(); } catch (err) { setError(err instanceof Error ? err.message : "Submit failed."); }
  }

  async function remove(id: string) {
    setError(null);
    if (!window.confirm("Delete this listing?")) return;
    try { await deleteOwnerListing(id); await load(); } catch (err) { setError(err instanceof Error ? err.message : "Delete failed."); }
  }

  return (
    <ProtectedRoute roles={["pg_owner"]}>
      <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex justify-between gap-4">
          <div><h1 className="text-3xl font-semibold">Your listings</h1><p className="mt-2 text-stone-600">Manage PG drafts, rooms, photos, and review submissions.</p></div>
          <Button asChild><Link href="/owner/listings/new">Add New PG</Link></Button>
        </div>
        {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}
        <div className="mt-8 grid gap-4">
          {items.length === 0 ? <EmptyState title="No listings yet" description="Create your first PG listing and add rooms and photos before review." /> : items.map((listing) => (
            <Card key={listing.id}>
              <CardHeader className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
                <div>
                  <CardTitle>{listing.pg_name}</CardTitle>
                  <CardDescription>{listing.address}</CardDescription>
                </div>
                <StatusBadge status={listing.status} />
              </CardHeader>
              <CardContent className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                <div className="grid gap-1 text-sm text-stone-600 sm:grid-cols-4 sm:gap-6">
                  <span>{rentRange(listing.monthly_rent_min, listing.monthly_rent_max)}</span>
                  <span>{listing.rooms_count} rooms</span>
                  <span>{listing.photos_count} photos</span>
                  <span>{new Date(listing.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button asChild variant="secondary"><Link href={`/owner/listings/${listing.id}`}>View/Edit</Link></Button>
                  {["draft", "rejected"].includes(listing.status) ? <Button onClick={() => submit(listing.id)}>Submit for Review</Button> : null}
                  {["draft", "rejected"].includes(listing.status) ? <Button variant="destructive" onClick={() => remove(listing.id)}>Delete</Button> : null}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </ProtectedRoute>
  );
}
