"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Coins, KeyRound, Search } from "lucide-react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/components/auth/auth-provider";
import { getUnlockedContacts, getWallet } from "@/lib/api-client";

export default function StudentDashboardPage() {
  const { user } = useAuth();
  const [balance, setBalance] = useState<number | null>(null);
  const [unlocks, setUnlocks] = useState<number>(0);
  useEffect(() => {
    Promise.all([getWallet(), getUnlockedContacts()])
      .then(([wallet, contacts]) => { setBalance(wallet.balance); setUnlocks(contacts.length); })
      .catch(() => undefined);
  }, []);
  return (
    <ProtectedRoute roles={["student"]}>
      <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-semibold tracking-normal">Welcome, {user?.full_name}</h1>
        <p className="mt-2 text-stone-600">Browse verified PGs, unlock contacts with credits, and revisit unlocked numbers anytime.</p>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <Card><CardHeader><Coins className="h-6 w-6 text-amber-600" /><CardTitle>{balance ?? "-"} credits</CardTitle><CardDescription>Available wallet balance</CardDescription></CardHeader></Card>
          <Card><CardHeader><KeyRound className="h-6 w-6 text-emerald-700" /><CardTitle>{unlocks}</CardTitle><CardDescription>Unlocked contacts</CardDescription></CardHeader></Card>
          <Card><CardHeader><Search className="h-6 w-6 text-stone-800" /><CardTitle>Find PGs</CardTitle><CardDescription>Approved listings near LPU</CardDescription></CardHeader></Card>
        </div>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button asChild><Link href="/pgs">Browse PGs</Link></Button>
          <Button asChild variant="secondary"><Link href="/student/credits">Add Credits</Link></Button>
          <Button asChild variant="secondary"><Link href="/student/unlocks">View Unlocked Contacts</Link></Button>
        </div>
      </main>
    </ProtectedRoute>
  );
}
