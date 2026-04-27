"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminUsersPage() {
  return <ProtectedRoute roles={["admin", "super_admin"]}><main className="mx-auto max-w-5xl px-4 py-12"><Card><CardHeader><CardTitle>Users</CardTitle><CardDescription>User moderation and role management placeholder for Part 2.</CardDescription></CardHeader></Card></main></ProtectedRoute>;
}
