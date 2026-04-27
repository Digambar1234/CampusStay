"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getReadyStatus } from "@/lib/api-client";
import type { ReadyResponse } from "@/lib/types";

export default function AdminSystemPage() {
  const [ready, setReady] = useState<ReadyResponse | null>(null);
  useEffect(() => { getReadyStatus().then(setReady).catch(() => undefined); }, []);
  return <ProtectedRoute roles={["admin","super_admin"]}><main className="mx-auto max-w-5xl px-4 py-12"><h1 className="text-3xl font-semibold">System readiness</h1><p className="mt-2 text-stone-600">Status: {ready?.status ?? "loading"}</p><div className="mt-8 grid gap-4 md:grid-cols-2">{ready && Object.entries(ready.checks).map(([name, check]) => <Card key={name}><CardHeader><CardTitle>{name}</CardTitle></CardHeader><CardContent><p className={check.ok ? "text-emerald-700" : "text-red-700"}>{check.ok ? "OK" : "Needs attention"}</p></CardContent></Card>)}</div></main></ProtectedRoute>;
}
