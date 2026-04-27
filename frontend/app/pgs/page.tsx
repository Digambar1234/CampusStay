"use client";

import { useEffect, useState } from "react";

import { PublicPGCard } from "@/components/pg/pg-card";
import { EmptyState, ErrorState } from "@/components/pg/state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getPublicPGs } from "@/lib/api-client";
import type { PGListing } from "@/lib/types";

export default function PGsPage() {
  const [items, setItems] = useState<PGListing[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load(query = "") {
    try {
      const data = await getPublicPGs(query);
      setItems(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load PGs.");
    }
  }
  useEffect(() => { load(); }, []);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const params = new URLSearchParams();
    for (const [key, value] of form.entries()) {
      if (value && value !== "any") params.set(key, String(value));
    }
    load(`?${params.toString()}`);
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div><p className="text-sm font-semibold uppercase text-emerald-700">Approved inventory</p><h1 className="mt-2 text-3xl font-semibold tracking-normal text-stone-950">Verified PGs near LPU</h1><p className="mt-3 max-w-2xl text-stone-600">Only admin-approved and verified PGs appear here. Owner phone numbers stay hidden until contact unlock ships.</p></div>
      <Card className="mt-8"><CardContent className="pt-5"><form className="grid gap-4 md:grid-cols-4" onSubmit={submit}><Field name="search" label="Search" /><Field name="min_price" label="Min budget" type="number" /><Field name="max_price" label="Max budget" type="number" /><Field name="max_distance_km" label="Max distance" type="number" step="0.1" /><Select name="gender_allowed" label="Gender" options={[["any","Any"],["boys","Boys"],["girls","Girls"],["co_living","Co-living"]]} /><Select name="sort" label="Sort" options={[["newest","Newest"],["price_low_to_high","Price low to high"],["price_high_to_low","Price high to low"],["distance_low_to_high","Distance low to high"]]} /><label className="flex items-end gap-2 text-sm"><input name="food_available" value="true" type="checkbox" /> Food</label><label className="flex items-end gap-2 text-sm"><input name="wifi_available" value="true" type="checkbox" /> Wi-Fi</label><label className="flex items-end gap-2 text-sm"><input name="ac_available" value="true" type="checkbox" /> AC</label><Button>Apply filters</Button></form></CardContent></Card>
      {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}
      <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{items.length === 0 ? <div className="md:col-span-2 lg:col-span-3"><EmptyState title="No approved PGs found" description="Try different filters or wait for admin-approved inventory." /></div> : items.map((pg) => <PublicPGCard key={pg.id} pg={pg} />)}</div>
    </main>
  );
}

function Field(props: React.InputHTMLAttributes<HTMLInputElement> & { label: string; name: string }) { const { label, name, ...rest } = props; return <div className="grid gap-2"><Label htmlFor={name}>{label}</Label><Input id={name} name={name} {...rest} /></div>; }
function Select({ name, label, options }: { name: string; label: string; options: [string, string][] }) { return <div className="grid gap-2"><Label>{label}</Label><select name={name} className="h-10 rounded-md border px-3">{options.map(([value,labelText]) => <option key={value} value={value}>{labelText}</option>)}</select></div>; }
