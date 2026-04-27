"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function ErrorPage() {
  return <main className="mx-auto max-w-xl px-4 py-20 text-center"><h1 className="text-3xl font-semibold">Something went wrong</h1><p className="mt-3 text-stone-600">Please try again in a moment.</p><div className="mt-6 flex justify-center gap-3"><Button asChild><Link href="/">Go home</Link></Button><Button asChild variant="secondary"><Link href="/pgs">Browse PGs</Link></Button></div></main>;
}
