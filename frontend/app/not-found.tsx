import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return <main className="mx-auto max-w-xl px-4 py-20 text-center"><h1 className="text-3xl font-semibold">Page not found</h1><p className="mt-3 text-stone-600">The page you are looking for does not exist.</p><div className="mt-6 flex justify-center gap-3"><Button asChild><Link href="/">Go home</Link></Button><Button asChild variant="secondary"><Link href="/pgs">Browse PGs</Link></Button></div></main>;
}
