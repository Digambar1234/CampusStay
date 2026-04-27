import { ArrowRight, BadgeCheck, Coins, Home, ShieldCheck, UsersRound } from "lucide-react";
import type React from "react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const studentSteps = ["Browse approved PGs", "Compare prices and facilities", "Unlock contact with one credit"];
const ownerSteps = ["Create owner account", "Submit PG details", "Go live after admin verification"];
const faqs = [
  ["Are PG contacts public?", "No. Owner phone numbers are unlocked only by logged-in students using credits."],
  ["Are listings guaranteed?", "Listings are verified to the best available process, but students should inspect the PG before rent or deposit."],
  ["Can owners list PGs?", "Yes. Owners submit details, rooms, and photos, then admins review before public listing."],
];

export default function HomePage() {
  return (
    <main>
      <section className="relative overflow-hidden bg-stone-950 text-white">
        <img
          src="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1800&q=80"
          alt="Modern student room with study desk"
          className="absolute inset-0 h-full w-full object-cover opacity-45"
        />
        <div className="relative mx-auto grid min-h-[680px] max-w-7xl content-center gap-10 px-4 py-20 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:px-8">
          <div className="max-w-3xl">
            <Badge className="bg-white/15 text-white ring-1 ring-white/25">Verified PG discovery near LPU</Badge>
            <h1 className="mt-6 max-w-4xl text-4xl font-semibold tracking-normal sm:text-6xl">
              Find verified PGs near LPU without walking door to door.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-stone-100">
              Browse real photos, compare prices, check facilities, and unlock owner contacts using credits.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/pgs">
                  Find PGs Near LPU <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="secondary">
                <Link href="/register">List Your PG</Link>
              </Button>
            </div>
          </div>
          <div className="self-end rounded-lg border border-white/20 bg-white/10 p-5 backdrop-blur">
            <div className="grid grid-cols-3 gap-3 text-center">
              <div>
                <p className="text-2xl font-semibold">10</p>
                <p className="text-xs text-stone-200">free credits</p>
              </div>
              <div>
                <p className="text-2xl font-semibold">1</p>
                <p className="text-xs text-stone-200">credit per unlock</p>
              </div>
              <div>
                <p className="text-2xl font-semibold">0</p>
                <p className="text-xs text-stone-200">duplicate charges</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
        {[
          ["The problem", "Students waste days visiting unverified PGs, comparing incomplete information, and calling owners without knowing real prices."],
          ["The product", "CampusStay creates a verified inventory layer for PGs near LPU with owner identity, admin checks, and structured room data."],
          ["The operating model", "Public browsing stays open. Contact access is gated behind credits so owner numbers are protected and unlocks are auditable."],
        ].map(([title, description]) => (
          <Card key={title}>
            <CardHeader>
              <CardTitle>{title}</CardTitle>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </section>

      <section className="bg-white py-16">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
          <Workflow title="For students" icon={<UsersRound className="h-5 w-5" />} steps={studentSteps} />
          <Workflow title="For PG owners" icon={<Home className="h-5 w-5" />} steps={ownerSteps} />
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-4 py-16 sm:px-6 md:grid-cols-2 lg:px-8">
        <Card>
          <CardHeader>
            <ShieldCheck className="h-9 w-9 text-emerald-700" aria-hidden="true" />
            <CardTitle>Trust and verification</CardTitle>
            <CardDescription>
              PG owner submissions start in pending review. Admins approve listings before they appear publicly, keeping the marketplace curated from day one.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <Coins className="h-9 w-9 text-amber-600" aria-hidden="true" />
            <CardTitle>Credit system</CardTitle>
            <CardDescription>
              Student signup creates a wallet with 10 free credits. Unlock history is unique per student and PG, so the same owner number is never charged twice.
            </CardDescription>
          </CardHeader>
        </Card>
      </section>

      <section className="bg-emerald-900 px-4 py-14 text-white">
        <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-6 sm:px-6 md:flex-row md:items-center lg:px-8">
          <div>
            <p className="text-2xl font-semibold">Start with verified inventory.</p>
            <p className="mt-2 max-w-2xl text-emerald-50">The Part 1 platform foundation is ready for real listings, approvals, credits, and payments in the next build phase.</p>
          </div>
          <Button asChild variant="secondary" size="lg">
            <Link href="/register">
              Create account <BadgeCheck className="h-4 w-4" aria-hidden="true" />
            </Link>
          </Button>
        </div>
      </section>
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-semibold">FAQ</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {faqs.map(([q, a]) => <Card key={q}><CardHeader><CardTitle>{q}</CardTitle><CardDescription>{a}</CardDescription></CardHeader></Card>)}
        </div>
      </section>
    </main>
  );
}

function Workflow({ title, icon, steps }: { title: string; icon: React.ReactNode; steps: string[] }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2 text-emerald-800">{icon}<CardTitle>{title}</CardTitle></div>
      </CardHeader>
      <CardContent>
        <ol className="grid gap-3">
          {steps.map((step, index) => (
            <li key={step} className="flex items-center gap-3 rounded-md border border-stone-200 p-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-stone-950 text-sm text-white">{index + 1}</span>
              <span className="text-sm font-medium text-stone-800">{step}</span>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
