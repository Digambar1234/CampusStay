"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ErrorState, LoadingState, rentRange } from "@/components/pg/state";
import { ContactRevealBox } from "@/components/pg/contact-reveal-box";
import { ReportForm } from "@/components/pg/report-form";
import { ReviewsSection } from "@/components/pg/reviews-section";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getPublicPG } from "@/lib/api-client";
import type { PGListing } from "@/lib/types";

export default function PGDetailsPage() {
  const params = useParams<{ id: string }>();
  const [pg, setPg] = useState<PGListing | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { getPublicPG(params.id).then(setPg).catch((err) => setError(err instanceof Error ? err.message : "Could not load PG.")); }, [params.id]);
  if (error) return <main className="mx-auto max-w-4xl px-4 py-12"><ErrorState message={error} /></main>;
  if (!pg) return <main className="mx-auto max-w-4xl px-4 py-12"><LoadingState /></main>;
  const facilities = [pg.food_available && "Food", pg.wifi_available && "Wi-Fi", pg.ac_available && "AC", pg.laundry_available && "Laundry", pg.parking_available && "Parking", pg.security_available && "Security"].filter(Boolean);
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="grid gap-4 md:grid-cols-3">{pg.photos.length ? pg.photos.map((photo) => <img key={photo.id} src={photo.image_url} alt={pg.pg_name} className="h-64 w-full rounded-lg object-cover" />) : <div className="flex h-64 items-center justify-center rounded-lg bg-stone-100 text-stone-500 md:col-span-3">No photos available</div>}</div>
      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_360px]">
        <section><div className="flex flex-wrap items-center gap-3"><h1 className="text-3xl font-semibold">{pg.pg_name}</h1><Badge>Verified</Badge></div><p className="mt-3 text-stone-600">{pg.description}</p><div className="mt-6 grid gap-3 text-sm text-stone-700"><p>Address: {pg.address}</p><p>Landmark: {pg.landmark ?? "-"}</p><p>Distance from LPU: {pg.distance_from_lpu_km ?? "-"} km</p><p>Gender: {pg.gender_allowed.replace("_", " ")}</p><p>Deposit: {pg.deposit_amount ?? "-"}</p></div><div className="mt-6 flex flex-wrap gap-2">{facilities.map((facility) => <span key={String(facility)} className="rounded-md bg-emerald-50 px-2 py-1 text-xs text-emerald-800">{facility}</span>)}</div></section>
        <div className="grid gap-4">
          <Card><CardHeader><CardTitle>{rentRange(pg.monthly_rent_min, pg.monthly_rent_max)}</CardTitle><CardDescription>Verified listing near LPU</CardDescription></CardHeader></Card>
          <ContactRevealBox pgId={pg.id} />
        </div>
      </div>
      <Card className="mt-8"><CardHeader><CardTitle>Room types and prices</CardTitle></CardHeader><CardContent className="grid gap-3">{pg.rooms.map((room) => <div key={room.id} className="rounded-md border p-3 text-sm">{room.room_type.replace("_"," ")} - {rentRange(room.price_per_month, null)} - {room.available_beds} beds {room.ac_available ? "- AC" : ""} {room.attached_washroom ? "- Attached washroom" : ""}</div>)}</CardContent></Card>
      <ReviewsSection pgId={pg.id} />
      <ReportForm pgId={pg.id} />
    </main>
  );
}
