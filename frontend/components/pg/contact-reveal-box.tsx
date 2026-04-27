"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/auth/auth-provider";
import { ErrorState } from "@/components/pg/state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getUnlockStatus, unlockContact } from "@/lib/api-client";
import type { UnlockContactResponse, UnlockStatus } from "@/lib/types";

export function whatsappHref(phone: string) {
  const digits = phone.replace(/\D/g, "");
  const normalized = digits.length === 10 ? `91${digits}` : digits;
  return `https://wa.me/${normalized}`;
}

export function ContactRevealBox({ pgId }: { pgId: string }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [status, setStatus] = useState<UnlockStatus | null>(null);
  const [contact, setContact] = useState<UnlockContactResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUnlocking, setIsUnlocking] = useState(false);

  useEffect(() => {
    if (!user || user.role !== "student") return;
    getUnlockStatus(pgId).then(setStatus).catch((err) => setError(err instanceof Error ? err.message : "Could not load unlock status."));
  }, [pgId, user]);

  async function reveal() {
    setError(null);
    setIsUnlocking(true);
    try {
      const response = await unlockContact(pgId);
      setContact(response);
      setStatus((previous) => previous ? { ...previous, is_unlocked: true, wallet_balance: response.remaining_balance, can_unlock: true } : previous);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unlock failed.");
    } finally {
      setIsUnlocking(false);
    }
  }

  if (isLoading) return <Card><CardHeader><CardTitle>Contact</CardTitle><CardDescription>Checking your account...</CardDescription></CardHeader></Card>;
  if (!user) return <Card><CardHeader><CardTitle>Owner contact is protected</CardTitle><CardDescription>Login as a student to unlock this PG owner contact.</CardDescription></CardHeader><CardContent><Button onClick={() => router.push("/login")}>Login to Unlock Owner Contact</Button></CardContent></Card>;
  if (user.role !== "student") return <Card><CardHeader><CardTitle>Student access required</CardTitle><CardDescription>Only student accounts can unlock PG owner contacts.</CardDescription></CardHeader></Card>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{contact ? "Owner contact" : "Unlock owner contact"}</CardTitle>
        <CardDescription>{status ? `${status.wallet_balance} credits available` : "1 credit = 1 contact unlock"}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3">
        {error ? <ErrorState message={error === "INSUFFICIENT_CREDITS" ? "You do not have enough credits." : error} /> : null}
        {contact ? (
          <div className="grid gap-2 text-sm">
            <p className="font-medium text-stone-950">Phone: {contact.owner_phone}</p>
            {contact.whatsapp_number ? <Button asChild variant="secondary"><a href={whatsappHref(contact.whatsapp_number)} target="_blank">Open WhatsApp</a></Button> : null}
            <Button asChild><a href={`tel:${contact.owner_phone}`}>Call owner</a></Button>
          </div>
        ) : status?.is_unlocked ? (
          <Button disabled={isUnlocking} onClick={reveal}>{isUnlocking ? "Loading..." : "Contact Already Unlocked"}</Button>
        ) : status && status.wallet_balance <= 0 ? (
          <>
            <p className="text-sm text-red-700">You do not have enough credits.</p>
            <Button asChild><Link href="/student/credits">Add 10 Credits for Rs. 10</Link></Button>
          </>
        ) : (
          <Button disabled={isUnlocking} onClick={reveal}>{isUnlocking ? "Unlocking..." : "Unlock Owner Contact - 1 Credit"}</Button>
        )}
      </CardContent>
    </Card>
  );
}
