"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getMyReviews } from "@/lib/api-client";
import type { Review } from "@/lib/types";

export default function StudentReviewsPage() {
  const [items, setItems] = useState<Review[]>([]);
  useEffect(() => { getMyReviews().then(setItems).catch(() => setItems([])); }, []);
  return <ProtectedRoute roles={["student"]}><main className="mx-auto max-w-6xl px-4 py-12"><h1 className="text-3xl font-semibold">My reviews</h1><div className="mt-8 grid gap-4">{items.map((review) => <Card key={review.id}><CardHeader><CardTitle>{review.pg_name} - {review.rating}/5</CardTitle></CardHeader><CardContent><p>{review.comment}</p><p className="mt-2 text-sm text-stone-500">Status: {review.status}</p></CardContent></Card>)}</div></main></ProtectedRoute>;
}
