"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { useAuth } from "@/components/auth/auth-provider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ProfilePage() {
  const { user } = useAuth();
  return (
    <ProtectedRoute roles={["student", "pg_owner", "admin", "super_admin"]}>
      <main className="mx-auto max-w-3xl px-4 py-12">
        <Card>
          <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
          <CardContent className="grid gap-2 text-sm">
            <p>Name: {user?.full_name}</p>
            <p>Email: {user?.email}</p>
            <p>Phone: {user?.phone ?? "-"}</p>
            <p>Role: {user?.role}</p>
            <p>Created: {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "-"}</p>
          </CardContent>
        </Card>
      </main>
    </ProtectedRoute>
  );
}
