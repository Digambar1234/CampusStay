"use client";

import { useEffect, useState } from "react";
import { AdminList } from "@/app/admin/pgs/pending/page";
import { useAuth } from "@/components/auth/auth-provider";
import { getAdminPGs } from "@/lib/api-client";
import type { PGListing } from "@/lib/types";

export default function ApprovedPGsPage() {
  const [items, setItems] = useState<PGListing[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isLoading: authLoading } = useAuth();

  async function load() {
    setError(null);
    setIsLoading(true);
    try {
      const data = await getAdminPGs("approved");
      setItems(data.items);
    } catch (err) {
      setItems([]);
      setError(err instanceof Error ? err.message : "Could not load approved PGs.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (!authLoading && user && ["admin", "super_admin"].includes(user.role)) {
      load();
    } else if (!authLoading) {
      setIsLoading(false);
    }
  }, [authLoading, user?.id, user?.role]);

  return <AdminList title="Approved PGs" description="Listings currently visible to students and public visitors." items={items} isLoading={isLoading} error={error} onRefresh={load} />;
}
