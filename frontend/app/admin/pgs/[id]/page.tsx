"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { ErrorState, LoadingState, rentRange } from "@/components/pg/state";
import { StatusBadge } from "@/components/pg/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { approvePG, getAdminPG, rejectPG, requestPGChanges, suspendPG } from "@/lib/api-client";
import type { PGListing } from "@/lib/types";

export default function AdminPGDetailPage() {
  const params = useParams<{ id: string }>();
  const [pg, setPg] = useState<PGListing | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  async function load() { try { setPg(await getAdminPG(params.id)); } catch (err) { setError(err instanceof Error ? err.message : "Could not load PG."); } }
  useEffect(() => { load(); }, [params.id]);
  async function action(run: () => Promise<PGListing>, success: string) { try { setPg(await run()); setMessage(success); } catch (err) { setError(err instanceof Error ? err.message : "Action failed."); } }
  return (
    <ProtectedRoute roles={["admin", "super_admin"]}>
      <main className="mx-auto max-w-7xl px-4 py-12">
        {error ? <ErrorState message={error} /> : null}{message ? <p className="mt-3 rounded-md bg-emerald-50 p-3 text-sm text-emerald-800">{message}</p> : null}
        {!pg ? <LoadingState /> : <div className="grid gap-6">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start"><div><h1 className="text-3xl font-semibold">{pg.pg_name}</h1><p className="mt-2 text-stone-600">{pg.address}</p></div><StatusBadge status={pg.status} /></div>
          <Card><CardHeader><CardTitle>Owner and contact</CardTitle><CardDescription>{pg.owner?.full_name} - {pg.owner?.email}</CardDescription></CardHeader><CardContent className="grid gap-2 text-sm"><p>Owner phone: {pg.owner_phone}</p><p>WhatsApp: {pg.whatsapp_number ?? "-"}</p><p>Admin verified: {pg.admin_verified ? "Yes" : "No"}</p></CardContent></Card>
          <Card><CardHeader><CardTitle>Listing details</CardTitle></CardHeader><CardContent className="grid gap-2 text-sm"><p>{pg.description}</p><p>Landmark: {pg.landmark ?? "-"}</p><p>Distance: {pg.distance_from_lpu_km ?? "-"} km</p><p>Rent: {rentRange(pg.monthly_rent_min, pg.monthly_rent_max)}</p><p>Deposit: {pg.deposit_amount ?? "-"}</p><p>Facilities: {[pg.food_available && "Food", pg.wifi_available && "Wi-Fi", pg.ac_available && "AC", pg.laundry_available && "Laundry", pg.parking_available && "Parking", pg.security_available && "Security"].filter(Boolean).join(", ") || "-"}</p></CardContent></Card>
          <Card><CardHeader><CardTitle>Rooms</CardTitle></CardHeader><CardContent className="grid gap-2">{pg.rooms.map((room) => <div key={room.id} className="rounded-md border p-3 text-sm">{room.room_type.replace("_"," ")} - {rentRange(room.price_per_month, null)} - {room.available_beds} beds</div>)}</CardContent></Card>
          <Card><CardHeader><CardTitle>Photos</CardTitle></CardHeader><CardContent className="grid gap-4 sm:grid-cols-3">{pg.photos.map((photo) => <img key={photo.id} src={photo.image_url} alt="" className="h-44 w-full rounded-md object-cover" />)}</CardContent></Card>
          <Card><CardHeader><CardTitle>Admin actions</CardTitle></CardHeader><CardContent className="flex flex-wrap gap-3"><Button onClick={() => action(() => approvePG(pg.id), "Listing approved.")}>Approve</Button><Button variant="secondary" onClick={() => { const reason = window.prompt("Rejection reason"); if (reason) action(() => rejectPG(pg.id, reason), "Listing rejected."); }}>Reject</Button><Button variant="secondary" onClick={() => { const note = window.prompt("Change request message"); if (note) action(() => requestPGChanges(pg.id, note), "Changes requested."); }}>Request Changes</Button><Button variant="destructive" onClick={() => { const reason = window.prompt("Suspension reason"); if (reason) action(() => suspendPG(pg.id, reason), "Listing suspended."); }}>Suspend</Button></CardContent></Card>
        </div>}
      </main>
    </ProtectedRoute>
  );
}
