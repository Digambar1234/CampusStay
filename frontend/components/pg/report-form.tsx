"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createReport } from "@/lib/api-client";
import type { ReportType } from "@/lib/types";

export function ReportForm({ pgId }: { pgId: string }) {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formState, setFormState] = useState({
    report_type: "fake_listing" as ReportType,
    reason: "",
    description: "",
    reporter_email: "",
    reporter_phone: "",
  });
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null); setMessage(null); setIsSubmitting(true);
    try {
      await createReport(pgId, {
        report_type: formState.report_type,
        reason: formState.reason,
        description: formState.description || null,
        reporter_email: formState.reporter_email || null,
        reporter_phone: formState.reporter_phone || null,
      });
      setFormState({ report_type: "fake_listing", reason: "", description: "", reporter_email: "", reporter_phone: "" });
      setMessage("Thanks. Our team will review this listing.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not submit report.");
    } finally {
      setIsSubmitting(false);
    }
  }
  return (
    <form className="mt-4 grid gap-3 rounded-md border p-4" onSubmit={submit}>
      <p className="font-medium">Report incorrect listing</p>
      <select name="report_type" value={formState.report_type} onChange={(event) => setFormState((current) => ({ ...current, report_type: event.target.value as ReportType }))} className="h-10 rounded-md border px-3"><option value="fake_listing">Fake listing</option><option value="wrong_price">Wrong price</option><option value="wrong_phone">Wrong phone</option><option value="room_not_available">Room not available</option><option value="misleading_photos">Misleading photos</option><option value="abusive_owner">Abusive owner</option><option value="other">Other</option></select>
      <Input name="reason" placeholder="Short reason" required value={formState.reason} onChange={(event) => setFormState((current) => ({ ...current, reason: event.target.value }))} />
      <Input name="description" placeholder="Description" value={formState.description} onChange={(event) => setFormState((current) => ({ ...current, description: event.target.value }))} />
      <div className="grid gap-2 sm:grid-cols-2"><div><Label>Email for public reports</Label><Input name="reporter_email" type="email" value={formState.reporter_email} onChange={(event) => setFormState((current) => ({ ...current, reporter_email: event.target.value }))} /></div><div><Label>Phone optional</Label><Input name="reporter_phone" value={formState.reporter_phone} onChange={(event) => setFormState((current) => ({ ...current, reporter_phone: event.target.value }))} /></div></div>
      {error ? <p className="text-sm text-red-700">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-700">{message}</p> : null}
      <Button type="submit" disabled={isSubmitting}>{isSubmitting ? "Submitting..." : "Submit report"}</Button>
    </form>
  );
}
