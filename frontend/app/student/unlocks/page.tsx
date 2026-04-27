"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { EmptyState, ErrorState, rentRange } from "@/components/pg/state";
import { whatsappHref } from "@/components/pg/contact-reveal-box";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getUnlockedContacts } from "@/lib/api-client";
import type { UnlockedContact } from "@/lib/types";

export default function StudentUnlocksPage() {
  const [items, setItems] = useState<UnlockedContact[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { getUnlockedContacts().then(setItems).catch((err) => setError(err instanceof Error ? err.message : "Could not load contacts.")); }, []);
  return (
    <ProtectedRoute roles={["student"]}>
      <main className="mx-auto max-w-6xl px-4 py-12">
        <h1 className="text-3xl font-semibold">Unlocked contacts</h1>
        <p className="mt-2 text-stone-600">Contacts you have unlocked are always available here without another credit charge.</p>
        {error ? <div className="mt-4"><ErrorState message={error} /></div> : null}
        <div className="mt-8 grid gap-4">
          {items.length === 0 ? <EmptyState title="No unlocked contacts yet" description="Browse approved PGs and unlock owner contacts with credits." /> : items.map((item) => (
            <Card key={item.pg_id}>
              <CardHeader className="flex flex-col gap-4 md:flex-row">
                {item.primary_photo_url ? <img src={item.primary_photo_url} alt={item.pg_name} className="h-28 w-full rounded-md object-cover md:w-40" /> : null}
                <div><CardTitle>{item.pg_name}</CardTitle><CardDescription>{item.address}</CardDescription></div>
              </CardHeader>
              <CardContent className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                <div className="text-sm text-stone-700">
                  <p>{rentRange(item.monthly_rent_min, item.monthly_rent_max)} - {item.distance_from_lpu_km ?? "-"} km</p>
                  <p>Phone: {item.owner_phone}</p>
                  <p>Unlocked: {new Date(item.unlocked_at).toLocaleDateString()}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button asChild><a href={`tel:${item.owner_phone}`}>Call</a></Button>
                  {item.whatsapp_number ? <Button asChild variant="secondary"><a href={whatsappHref(item.whatsapp_number)} target="_blank">WhatsApp</a></Button> : null}
                  <Button asChild variant="secondary"><Link href={`/pgs/${item.pg_id}`}>View PG</Link></Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </ProtectedRoute>
  );
}
