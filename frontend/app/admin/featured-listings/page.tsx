"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { adminCancelFeaturedListing, adminCreateFeaturedListing, adminGetFeaturedListings, getAdminPGs } from "@/lib/api-client";
import type { FeaturedListing, PGListing } from "@/lib/types";

export default function AdminFeaturedListingsPage() {
  const [items, setItems] = useState<FeaturedListing[]>([]);
  const [pgs, setPgs] = useState<PGListing[]>([]);
  const [formState, setFormState] = useState({ pg_id: "", days: "7", amount_rupees: "0" });
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function load() { setItems(await adminGetFeaturedListings()); setPgs((await getAdminPGs("approved")).items); }
  useEffect(() => { load().catch(() => undefined); }, []);
  useEffect(() => {
    if (!formState.pg_id && pgs[0]) setFormState((current) => ({ ...current, pg_id: pgs[0].id }));
  }, [formState.pg_id, pgs]);
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null); setMessage(null);
    try {
      await adminCreateFeaturedListing({ pg_id: formState.pg_id, days: Number(formState.days), amount_rupees: Number(formState.amount_rupees || 0), source: "admin_grant" });
      setFormState((current) => ({ ...current, days: "7", amount_rupees: "0" }));
      await load();
      setMessage("Featured listing added.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add featured listing.");
    }
  }
  return <ProtectedRoute roles={["admin","super_admin"]}><main className="mx-auto max-w-7xl px-4 py-12"><h1 className="text-3xl font-semibold">Featured listings</h1>{error ? <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}{message ? <p className="mt-4 rounded-md bg-emerald-50 p-3 text-sm text-emerald-700">{message}</p> : null}<Card className="mt-8"><CardHeader><CardTitle>Add featured listing</CardTitle></CardHeader><CardContent><form className="grid gap-3 md:grid-cols-4" onSubmit={submit}><select name="pg_id" value={formState.pg_id} onChange={(event) => setFormState((current) => ({ ...current, pg_id: event.target.value }))} className="h-10 rounded-md border px-3">{pgs.map((pg) => <option key={pg.id} value={pg.id}>{pg.pg_name}</option>)}</select><div><Label>Days</Label><Input name="days" type="number" value={formState.days} onChange={(event) => setFormState((current) => ({ ...current, days: event.target.value }))} /></div><div><Label>Amount</Label><Input name="amount_rupees" type="number" value={formState.amount_rupees} onChange={(event) => setFormState((current) => ({ ...current, amount_rupees: event.target.value }))} /></div><Button type="submit">Add</Button></form></CardContent></Card><div className="mt-8 grid gap-4">{items.map((item) => <Card key={item.id}><CardHeader><CardTitle>{item.pg_name}</CardTitle></CardHeader><CardContent className="flex justify-between text-sm"><span>{item.status} until {new Date(item.ends_at).toLocaleDateString()}</span><Button type="button" variant="destructive" onClick={async () => { await adminCancelFeaturedListing(item.id); await load(); }}>Cancel</Button></CardContent></Card>)}</div></main></ProtectedRoute>;
}
