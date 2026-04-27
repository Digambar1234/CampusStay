"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { ErrorState, LoadingState, rentRange } from "@/components/pg/state";
import { StatusBadge } from "@/components/pg/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  addRoom,
  deletePhoto,
  deleteRoom,
  getOwnerListing,
  markPrimaryPhoto,
  submitOwnerListing,
  updateOwnerListing,
  uploadPhoto,
  type ListingPayload,
} from "@/lib/api-client";
import type { ImageType, PGListing, RoomType } from "@/lib/types";

export default function OwnerListingEditPage() {
  const params = useParams<{ id: string }>();
  const [listing, setListing] = useState<PGListing | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [roomForm, setRoomForm] = useState({
    room_type: "single" as RoomType,
    price_per_month: "",
    available_beds: "",
    ac_available: false,
    attached_washroom: false,
  });
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoType, setPhotoType] = useState<ImageType>("room");
  const [photoIsPrimary, setPhotoIsPrimary] = useState(false);
  const [isAddingRoom, setIsAddingRoom] = useState(false);
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);

  async function load() {
    try {
      const refreshedListing = await getOwnerListing(params.id);
      setListing(refreshedListing);
      return refreshedListing;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load listing.");
      return null;
    }
  }
  useEffect(() => { load(); }, [params.id]);

  if (!listing && !error) return <ProtectedRoute roles={["pg_owner"]}><main className="mx-auto max-w-6xl px-4 py-12"><LoadingState /></main></ProtectedRoute>;

  const isApproved = listing?.status === "approved";
  const ready = Boolean(listing && listing.pg_name && listing.address && listing.owner_phone && listing.rooms.length > 0 && listing.photos.length > 0);

  async function saveDetails(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!listing) return;
    setError(null); setMessage(null);
    const form = new FormData(event.currentTarget);
    const payload: Partial<ListingPayload> = {
      pg_name: String(form.get("pg_name")),
      description: String(form.get("description") || "") || null,
      address: String(form.get("address")),
      landmark: String(form.get("landmark") || "") || null,
      distance_from_lpu_km: form.get("distance_from_lpu_km") ? Number(form.get("distance_from_lpu_km")) : null,
      gender_allowed: String(form.get("gender_allowed")) as ListingPayload["gender_allowed"],
      food_available: form.has("food_available"),
      wifi_available: form.has("wifi_available"),
      ac_available: form.has("ac_available"),
      laundry_available: form.has("laundry_available"),
      parking_available: form.has("parking_available"),
      security_available: form.has("security_available"),
      monthly_rent_min: form.get("monthly_rent_min") ? Number(form.get("monthly_rent_min")) : null,
      monthly_rent_max: form.get("monthly_rent_max") ? Number(form.get("monthly_rent_max")) : null,
      deposit_amount: form.get("deposit_amount") ? Number(form.get("deposit_amount")) : null,
      owner_phone: String(form.get("owner_phone")),
      whatsapp_number: String(form.get("whatsapp_number") || "") || null,
    };
    try { setListing(await updateOwnerListing(listing.id, payload)); setMessage("Listing details saved."); } catch (err) { setError(err instanceof Error ? err.message : "Save failed."); }
  }

  async function createRoom(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!listing) return;
    setError(null); setMessage(null);
    const price = Number(roomForm.price_per_month);
    const beds = Number(roomForm.available_beds || 0);
    if (!price || price <= 0) {
      setError("Enter a valid monthly room price.");
      return;
    }
    if (beds < 0) {
      setError("Available beds cannot be negative.");
      return;
    }
    setIsAddingRoom(true);
    try {
      await addRoom(listing.id, {
        room_type: roomForm.room_type,
        price_per_month: price,
        available_beds: beds,
        ac_available: roomForm.ac_available,
        attached_washroom: roomForm.attached_washroom,
      });
      setRoomForm({ room_type: "single", price_per_month: "", available_beds: "", ac_available: false, attached_washroom: false });
      await load();
      setMessage("Room added.");
    } catch (err) { setError(err instanceof Error ? err.message : "Room add failed."); }
    finally { setIsAddingRoom(false); }
  }

  async function photoUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!listing) return;
    setError(null); setMessage(null);
    if (!photoFile) {
      setError("Select a photo before uploading.");
      return;
    }
    setIsUploadingPhoto(true);
    try {
      await uploadPhoto(listing.id, { file: photoFile, image_type: photoType, is_primary: photoIsPrimary });
      setPhotoFile(null);
      setPhotoType("room");
      setPhotoIsPrimary(false);
      await load();
      setMessage("Photo uploaded.");
    } catch (err) { setError(err instanceof Error ? err.message : "Photo upload failed."); }
    finally { setIsUploadingPhoto(false); }
  }

  async function submitForReview() {
    if (!listing) return;
    setError(null); setMessage(null); setIsSubmittingReview(true);
    try {
      const latestListing = await load();
      if (!latestListing) return;
      if (!latestListing.rooms.length || !latestListing.photos.length) {
        setError("Add at least one room and one photo before submitting.");
        return;
      }
      setListing(await submitOwnerListing(latestListing.id));
      setMessage("Submitted for admin review.");
    } catch (err) { setError(err instanceof Error ? err.message : "Submit failed."); }
    finally { setIsSubmittingReview(false); }
  }

  return (
    <ProtectedRoute roles={["pg_owner"]}>
      <main className="mx-auto max-w-6xl px-4 py-12">
        {error ? <ErrorState message={error} /> : null}
        {message ? <p className="mt-3 rounded-md bg-emerald-50 p-3 text-sm text-emerald-800">{message}</p> : null}
        {listing ? (
          <div className="mt-6 grid gap-6">
            <div className="flex items-center justify-between"><h1 className="text-3xl font-semibold">{listing.pg_name}</h1><StatusBadge status={listing.status} /></div>
            {isApproved ? <ErrorState message="Approved listings cannot be edited directly in this version." /> : null}
            <Card><CardHeader><CardTitle>Listing Details</CardTitle><CardDescription>Update core listing details and facilities.</CardDescription></CardHeader><CardContent><form className="grid gap-4" onSubmit={saveDetails}><div className="grid gap-4 sm:grid-cols-2"><Field name="pg_name" label="PG name" defaultValue={listing.pg_name} disabled={isApproved} /><Field name="description" label="Description" defaultValue={listing.description ?? ""} disabled={isApproved} /><Field name="address" label="Address" defaultValue={listing.address} disabled={isApproved} /><Field name="landmark" label="Landmark" defaultValue={listing.landmark ?? ""} disabled={isApproved} /><Field name="distance_from_lpu_km" label="Distance from LPU" type="number" step="0.01" defaultValue={listing.distance_from_lpu_km ?? ""} disabled={isApproved} /><select name="gender_allowed" defaultValue={listing.gender_allowed} disabled={isApproved} className="h-10 rounded-md border px-3"><option value="boys">Boys</option><option value="girls">Girls</option><option value="co_living">Co-living</option></select><Field name="monthly_rent_min" label="Minimum rent" type="number" defaultValue={listing.monthly_rent_min ?? ""} disabled={isApproved} /><Field name="monthly_rent_max" label="Maximum rent" type="number" defaultValue={listing.monthly_rent_max ?? ""} disabled={isApproved} /><Field name="deposit_amount" label="Deposit" type="number" defaultValue={listing.deposit_amount ?? ""} disabled={isApproved} /><Field name="owner_phone" label="Owner phone" defaultValue={listing.owner_phone ?? ""} disabled={isApproved} /><Field name="whatsapp_number" label="WhatsApp" defaultValue={listing.whatsapp_number ?? ""} disabled={isApproved} /></div><div className="grid gap-2 sm:grid-cols-3">{["food_available","wifi_available","ac_available","laundry_available","parking_available","security_available"].map((key) => <label key={key} className="flex gap-2 text-sm"><input name={key} type="checkbox" defaultChecked={Boolean(listing[key as keyof PGListing])} disabled={isApproved} /> {key.replace("_"," ")}</label>)}</div><Button disabled={isApproved}>Save Details</Button></form></CardContent></Card>
            <Card><CardHeader><CardTitle>Rooms</CardTitle><CardDescription>Add at least one room before submission.</CardDescription></CardHeader><CardContent className="grid gap-4"><form className="grid gap-3 sm:grid-cols-5" onSubmit={createRoom}><select name="room_type" value={roomForm.room_type} onChange={(event) => setRoomForm((current) => ({ ...current, room_type: event.target.value as RoomType }))} className="h-10 rounded-md border px-3" disabled={isApproved}><option value="single">Single</option><option value="double_sharing">Double sharing</option><option value="triple_sharing">Triple sharing</option><option value="four_sharing">Four sharing</option><option value="dormitory">Dormitory</option></select><Input name="price_per_month" type="number" placeholder="Price" value={roomForm.price_per_month} onChange={(event) => setRoomForm((current) => ({ ...current, price_per_month: event.target.value }))} disabled={isApproved} /><Input name="available_beds" type="number" placeholder="Beds" value={roomForm.available_beds} onChange={(event) => setRoomForm((current) => ({ ...current, available_beds: event.target.value }))} disabled={isApproved} /><label className="flex items-center gap-2 text-sm"><input name="room_ac" type="checkbox" checked={roomForm.ac_available} onChange={(event) => setRoomForm((current) => ({ ...current, ac_available: event.target.checked }))} disabled={isApproved} /> AC</label><Button type="submit" disabled={isApproved || isAddingRoom}>{isAddingRoom ? "Adding..." : "Add room"}</Button><label className="flex items-center gap-2 text-sm"><input name="attached_washroom" type="checkbox" checked={roomForm.attached_washroom} onChange={(event) => setRoomForm((current) => ({ ...current, attached_washroom: event.target.checked }))} disabled={isApproved} /> Attached washroom</label></form>{listing.rooms.map((room) => <div key={room.id} className="flex justify-between rounded-md border p-3 text-sm"><span>{room.room_type.replace("_"," ")} - {rentRange(room.price_per_month, null)} - {room.available_beds} beds</span><Button type="button" variant="destructive" size="sm" disabled={isApproved} onClick={async () => { setError(null); setMessage(null); try { await deleteRoom(listing.id, room.id); await load(); setMessage("Room deleted."); } catch (err) { setError(err instanceof Error ? err.message : "Room delete failed."); } }}>Delete</Button></div>)}</CardContent></Card>
            <Card><CardHeader><CardTitle>Photos</CardTitle><CardDescription>Upload real PG photos to Cloudinary.</CardDescription></CardHeader><CardContent className="grid gap-4"><form className="grid gap-3 sm:grid-cols-4" onSubmit={photoUpload}><Input key={photoFile ? "photo-selected" : "photo-empty"} name="file" type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => setPhotoFile(event.target.files?.[0] ?? null)} disabled={isApproved} /><select name="image_type" value={photoType} onChange={(event) => setPhotoType(event.target.value as ImageType)} className="h-10 rounded-md border px-3" disabled={isApproved}><option value="room">Room</option><option value="washroom">Washroom</option><option value="building">Building</option><option value="mess">Mess</option><option value="common_area">Common area</option><option value="other">Other</option></select><label className="flex items-center gap-2 text-sm"><input name="is_primary" type="checkbox" checked={photoIsPrimary} onChange={(event) => setPhotoIsPrimary(event.target.checked)} disabled={isApproved} /> Primary</label><Button type="submit" disabled={isApproved || isUploadingPhoto}>{isUploadingPhoto ? "Uploading..." : "Upload"}</Button></form><div className="grid gap-4 sm:grid-cols-3">{listing.photos.map((photo) => <div key={photo.id} className="rounded-md border p-3"><img src={photo.image_url} alt={`${listing.pg_name} ${photo.image_type}`} className="h-36 w-full rounded-md object-cover" /><p className="mt-2 text-sm">{photo.image_type} {photo.is_primary ? "(primary)" : ""}</p><div className="mt-2 flex gap-2"><Button type="button" size="sm" variant="secondary" disabled={isApproved} onClick={async () => { setError(null); setMessage(null); try { await markPrimaryPhoto(listing.id, photo.id); await load(); setMessage("Primary photo updated."); } catch (err) { setError(err instanceof Error ? err.message : "Primary photo update failed."); } }}>Primary</Button><Button type="button" size="sm" variant="destructive" disabled={isApproved} onClick={async () => { setError(null); setMessage(null); try { await deletePhoto(listing.id, photo.id); await load(); setMessage("Photo deleted."); } catch (err) { setError(err instanceof Error ? err.message : "Photo delete failed."); } }}>Delete</Button></div></div>)}</div></CardContent></Card>
            <Card><CardHeader><CardTitle>Submit for Review</CardTitle><CardDescription>Admin approval is required before the listing is public.</CardDescription></CardHeader><CardContent className="grid gap-3 text-sm"><Check ok={Boolean(listing.pg_name && listing.address && listing.owner_phone)} label="Required details completed" /><Check ok={listing.rooms.length > 0} label="At least one room added" /><Check ok={listing.photos.length > 0} label="At least one photo uploaded" /><Button type="button" disabled={!ready || isApproved || isSubmittingReview} onClick={submitForReview}>{isSubmittingReview ? "Submitting..." : "Submit for Review"}</Button></CardContent></Card>
          </div>
        ) : null}
      </main>
    </ProtectedRoute>
  );
}

function Field(props: React.InputHTMLAttributes<HTMLInputElement> & { label: string; name: string }) { const { label, name, ...rest } = props; return <div className="grid gap-2"><Label htmlFor={name}>{label}</Label><Input id={name} name={name} {...rest} /></div>; }
function Check({ ok, label }: { ok: boolean; label: string }) { return <p className={ok ? "text-emerald-700" : "text-red-700"}>{ok ? "Ready" : "Missing"}: {label}</p>; }
