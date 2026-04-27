"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getMyReports } from "@/lib/api-client";
import type { Report } from "@/lib/types";

export default function StudentReportsPage() {
  const [items, setItems] = useState<Report[]>([]);
  useEffect(() => { getMyReports().then(setItems).catch(() => setItems([])); }, []);
  return <ProtectedRoute roles={["student"]}><main className="mx-auto max-w-6xl px-4 py-12"><h1 className="text-3xl font-semibold">My reports</h1><div className="mt-8 grid gap-4">{items.map((report) => <Card key={report.id}><CardHeader><CardTitle>{report.pg_name}</CardTitle></CardHeader><CardContent><p>{report.report_type.replace("_"," ")} - {report.status}</p><p className="text-sm text-stone-600">{report.reason}</p></CardContent></Card>)}</div></main></ProtectedRoute>;
}
