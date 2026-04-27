"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { adminApproveReview, adminGetReviews, adminHideReview, adminRejectReview } from "@/lib/api-client";
import type { Review } from "@/lib/types";

export default function AdminReviewsPage() {
  const [items, setItems] = useState<Review[]>([]);
  async function load() { setItems(await adminGetReviews()); }
  useEffect(() => { load().catch(() => undefined); }, []);
  async function act(fn: () => Promise<unknown>) { await fn(); await load(); }
  return <ProtectedRoute roles={["admin","super_admin"]}><main className="mx-auto max-w-7xl px-4 py-12"><h1 className="text-3xl font-semibold">Review moderation</h1><div className="mt-8 grid gap-4">{items.map((r) => <Card key={r.id}><CardHeader><CardTitle>{r.pg_name} - {r.rating}/5</CardTitle></CardHeader><CardContent className="grid gap-2 text-sm"><p>{r.comment}</p><p>{r.student_name} - {r.student_email} - {r.status}</p><div className="flex gap-2"><Button onClick={() => act(() => adminApproveReview(r.id))}>Approve</Button><Button variant="secondary" onClick={() => act(() => adminHideReview(r.id))}>Hide</Button><Button variant="destructive" onClick={() => act(() => adminRejectReview(r.id))}>Reject</Button></div></CardContent></Card>)}</div></main></ProtectedRoute>;
}
