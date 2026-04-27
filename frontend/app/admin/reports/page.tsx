"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { adminGetReports, adminResolveReport, adminUpdateReport } from "@/lib/api-client";
import type { Report } from "@/lib/types";

export default function AdminReportsPage() {
  const [items, setItems] = useState<Report[]>([]);
  async function load() { setItems(await adminGetReports()); }
  useEffect(() => { load().catch(() => undefined); }, []);
  return <ProtectedRoute roles={["admin","super_admin"]}><main className="mx-auto max-w-7xl px-4 py-12"><h1 className="text-3xl font-semibold">Reports</h1><div className="mt-8 grid gap-4">{items.map((r) => <Card key={r.id}><CardHeader><CardTitle>{r.pg_name} - {r.report_type.replace("_"," ")}</CardTitle></CardHeader><CardContent className="grid gap-2 text-sm"><p>{r.reason}</p><p>{r.description}</p><p>Status: {r.status} Priority: {r.priority}</p><p>Reporter: {r.reporter_email ?? r.student_id ?? "anonymous"}</p><div className="flex gap-2"><Button variant="secondary" onClick={async () => { await adminUpdateReport(r.id, { status: "reviewed" }); await load(); }}>Mark reviewed</Button><Button onClick={async () => { await adminResolveReport(r.id); await load(); }}>Resolve</Button><Button variant="destructive" onClick={async () => { await adminUpdateReport(r.id, { status: "rejected" }); await load(); }}>Reject</Button></div></CardContent></Card>)}</div></main></ProtectedRoute>;
}
