"use client";

import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAuditLogs } from "@/lib/api-client";
import type { AuditLog } from "@/lib/types";

export default function AuditLogsPage() {
  const [items, setItems] = useState<AuditLog[]>([]);
  useEffect(() => { getAuditLogs().then((data) => setItems(data.items)).catch(() => setItems([])); }, []);
  return <ProtectedRoute roles={["admin","super_admin"]}><main className="mx-auto max-w-7xl px-4 py-12"><h1 className="text-3xl font-semibold">Audit logs</h1><div className="mt-8 grid gap-3">{items.map((log) => <Card key={log.id}><CardHeader><CardTitle>{log.action}</CardTitle></CardHeader><CardContent className="grid gap-1 text-sm"><p>{log.admin_name} - {log.admin_email}</p><p>{log.target_type}: {log.target_id ?? "-"}</p><p>{new Date(log.created_at).toLocaleString()}</p><pre className="overflow-auto rounded bg-stone-100 p-2 text-xs">{JSON.stringify(log.metadata ?? {}, null, 2)}</pre></CardContent></Card>)}</div></main></ProtectedRoute>;
}
