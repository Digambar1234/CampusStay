"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createOwnerListing, type ListingPayload } from "@/lib/api-client";

function value(form: FormData, key: string) { const raw = String(form.get(key) ?? ""); return raw.trim(); }
function num(form: FormData, key: string) { const raw = value(form, key); return raw ? Number(raw) : null; }

export default function NewOwnerListingPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const form = new FormData(event.currentTarget);
    const payload: ListingPayload = {
      pg_name: value(form, "pg_name"),
      description: value(form, "description") || null,
      address: value(form, "address"),
      landmark: value(form, "landmark") || null,
      distance_from_lpu_km: num(form, "distance_from_lpu_km"),
      latitude: num(form, "latitude"),
      longitude: num(form, "longitude"),
      gender_allowed: value(form, "gender_allowed") as ListingPayload["gender_allowed"],
      food_available: form.has("food_available"),
      wifi_available: form.has("wifi_available"),
      ac_available: form.has("ac_available"),
      laundry_available: form.has("laundry_available"),
      parking_available: form.has("parking_available"),
      security_available: form.has("security_available"),
      monthly_rent_min: num(form, "monthly_rent_min"),
      monthly_rent_max: num(form, "monthly_rent_max"),
      deposit_amount: num(form, "deposit_amount"),
      owner_phone: value(form, "owner_phone"),
      whatsapp_number: value(form, "whatsapp_number") || null,
    };
    try {
      const created = await createOwnerListing(payload);
      router.push(`/owner/listings/${created.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create listing.");
    }
  }

  return (
    <ProtectedRoute roles={["pg_owner"]}>
      <main className="mx-auto max-w-5xl px-4 py-12">
        <Card>
          <CardHeader><CardTitle>Add New PG</CardTitle><CardDescription>Save the listing as a draft, then add rooms and photos before review.</CardDescription></CardHeader>
          <CardContent>
            <form className="grid gap-8" onSubmit={submit}>
              <Section title="Basic Information"><Field name="pg_name" label="PG name" required /><Field name="description" label="Description" /><Field name="address" label="Address" required /><Field name="landmark" label="Landmark" /><Field name="distance_from_lpu_km" label="Distance from LPU in km" type="number" step="0.01" /></Section>
              <Section title="Location"><Field name="latitude" label="Latitude" type="number" step="0.0000001" /><Field name="longitude" label="Longitude" type="number" step="0.0000001" /></Section>
              <Section title="Category"><Label>Gender allowed</Label><select name="gender_allowed" className="h-10 rounded-md border px-3"><option value="boys">Boys</option><option value="girls">Girls</option><option value="co_living">Co-living</option></select></Section>
              <Section title="Facilities"><Checks names={["food_available", "wifi_available", "ac_available", "laundry_available", "parking_available", "security_available"]} /></Section>
              <Section title="Pricing"><Field name="monthly_rent_min" label="Minimum monthly rent" type="number" /><Field name="monthly_rent_max" label="Maximum monthly rent" type="number" /><Field name="deposit_amount" label="Deposit amount" type="number" /></Section>
              <Section title="Contact"><Field name="owner_phone" label="Owner phone" required /><Field name="whatsapp_number" label="WhatsApp number" /></Section>
              {error ? <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}
              <div className="flex gap-3"><Button type="submit">Save as Draft</Button><Button type="submit" variant="secondary">Save and Continue to Rooms</Button></div>
            </form>
          </CardContent>
        </Card>
      </main>
    </ProtectedRoute>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) { return <section className="grid gap-4"><h2 className="text-lg font-semibold">{title}</h2><div className="grid gap-4 sm:grid-cols-2">{children}</div></section>; }
function Field(props: React.InputHTMLAttributes<HTMLInputElement> & { label: string; name: string }) { const { label, name, ...rest } = props; return <div className="grid gap-2"><Label htmlFor={name}>{label}</Label><Input id={name} name={name} {...rest} /></div>; }
function Checks({ names }: { names: string[] }) { return <>{names.map((name) => <label key={name} className="flex items-center gap-2 text-sm"><input name={name} type="checkbox" /> {name.replace("_", " ")}</label>)}</>; }
