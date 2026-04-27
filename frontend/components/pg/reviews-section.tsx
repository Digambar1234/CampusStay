"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/components/auth/auth-provider";
import { ErrorState } from "@/components/pg/state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createReview, getPGReviews, getUnlockStatus } from "@/lib/api-client";
import type { Review } from "@/lib/types";

export function ReviewsSection({ pgId }: { pgId: string }) {
  const { user } = useAuth();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [average, setAverage] = useState<number | null>(null);
  const [canReview, setCanReview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formState, setFormState] = useState({ rating: "5", title: "", comment: "" });

  async function load() {
    const data = await getPGReviews(pgId);
    setReviews(data.items);
    setAverage(data.average_rating);
    if (user?.role === "student") {
      const status = await getUnlockStatus(pgId);
      setCanReview(status.is_unlocked);
    }
  }

  useEffect(() => { load().catch(() => undefined); }, [pgId, user?.id]);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null); setMessage(null); setIsSubmitting(true);
    try {
      await createReview(pgId, { rating: Number(formState.rating), title: formState.title || null, comment: formState.comment });
      setFormState({ rating: "5", title: "", comment: "" });
      setMessage("Review submitted.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not submit review.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card className="mt-8">
      <CardHeader><CardTitle>Reviews</CardTitle><CardDescription>{average ? `${average}/5 average from ${reviews.length} reviews` : "No reviews yet"}</CardDescription></CardHeader>
      <CardContent className="grid gap-5">
        {reviews.map((review) => <div key={review.id} className="rounded-md border p-3"><p className="font-medium">{review.rating}/5 {review.title}</p><p className="mt-1 text-sm text-stone-700">{review.comment}</p><p className="mt-2 text-xs text-stone-500">By {review.reviewer_name ?? "Student"}</p></div>)}
        {!user ? <p className="text-sm text-stone-600">Login as student to review after unlocking contact.</p> : user.role !== "student" ? <p className="text-sm text-stone-600">Only students can review PGs.</p> : !canReview ? <p className="text-sm text-stone-600">Unlock this PG contact before leaving a review.</p> : (
          <form className="grid gap-3" onSubmit={submit}>
            <div className="grid gap-2"><Label>Rating</Label><select name="rating" value={formState.rating} onChange={(event) => setFormState((current) => ({ ...current, rating: event.target.value }))} className="h-10 rounded-md border px-3">{[5,4,3,2,1].map((rating) => <option key={rating} value={rating}>{rating}</option>)}</select></div>
            <div className="grid gap-2"><Label>Title</Label><Input name="title" value={formState.title} onChange={(event) => setFormState((current) => ({ ...current, title: event.target.value }))} /></div>
            <div className="grid gap-2"><Label>Comment</Label><Input name="comment" required minLength={5} value={formState.comment} onChange={(event) => setFormState((current) => ({ ...current, comment: event.target.value }))} /></div>
            {error ? <ErrorState message={error} /> : null}{message ? <p className="text-sm text-emerald-700">{message}</p> : null}
            <Button type="submit" disabled={isSubmitting}>{isSubmitting ? "Submitting..." : "Submit review"}</Button>
          </form>
        )}
      </CardContent>
    </Card>
  );
}
