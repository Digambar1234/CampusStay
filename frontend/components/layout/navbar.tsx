"use client";

import { Building2, Menu, ShieldCheck, UserRound } from "lucide-react";
import Link from "next/link";

import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const { user, signOut } = useAuth();
  const dashboardHref =
    user?.role === "student"
      ? "/student/dashboard"
      : user?.role === "pg_owner"
        ? "/owner/dashboard"
        : user
          ? "/admin/dashboard"
          : "/login";

  return (
    <header className="sticky top-0 z-40 border-b border-stone-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold text-stone-950">
          <Building2 className="h-5 w-5 text-emerald-700" aria-hidden="true" />
          CampusStay
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-medium text-stone-700 md:flex">
          <Link href="/pgs" className="hover:text-stone-950">PGs</Link>
          <Link href="/owner/listings/new" className="hover:text-stone-950">List Your PG</Link>
          {user?.role === "student" ? <Link href="/student/credits" className="hover:text-stone-950">Credits</Link> : null}
          {user?.role === "student" ? <Link href="/student/unlocks" className="hover:text-stone-950">My Unlocks</Link> : null}
          {user?.role === "student" ? <Link href="/student/reviews" className="hover:text-stone-950">Reviews</Link> : null}
          {user?.role === "student" ? <Link href="/student/reports" className="hover:text-stone-950">Reports</Link> : null}
          {user?.role === "pg_owner" ? <Link href="/owner/analytics" className="hover:text-stone-950">Analytics</Link> : null}
          {user && ["admin", "super_admin"].includes(user.role) ? <Link href="/admin/analytics" className="hover:text-stone-950">Analytics</Link> : null}
          {user && ["admin", "super_admin"].includes(user.role) ? <Link href="/admin/reviews" className="hover:text-stone-950">Reviews</Link> : null}
          {user && ["admin", "super_admin"].includes(user.role) ? <Link href="/admin/reports" className="hover:text-stone-950">Reports</Link> : null}
          {user && ["admin", "super_admin"].includes(user.role) ? <Link href="/admin/featured-listings" className="hover:text-stone-950">Featured</Link> : null}
          {user && ["admin", "super_admin"].includes(user.role) ? <Link href="/admin/audit-logs" className="hover:text-stone-950">Audit</Link> : null}
          {user && ["admin", "super_admin"].includes(user.role) ? <Link href="/admin/system" className="hover:text-stone-950">System</Link> : null}
          <Link href="/admin/login" className="inline-flex items-center gap-1 hover:text-stone-950">
            <ShieldCheck className="h-4 w-4" aria-hidden="true" />
            Admin
          </Link>
        </nav>
        <div className="flex items-center gap-2">
          {user ? (
            <>
              <Button asChild variant="ghost" className="hidden sm:inline-flex">
                <Link href={dashboardHref}>
                  <UserRound className="h-4 w-4" aria-hidden="true" />
                  Dashboard
                </Link>
              </Button>
              <Button asChild variant="ghost" className="hidden sm:inline-flex">
                <Link href="/profile">Profile</Link>
              </Button>
              <Button variant="secondary" onClick={signOut}>Logout</Button>
            </>
          ) : (
            <>
              <Button asChild variant="ghost" className="hidden sm:inline-flex">
                <Link href="/login">Login</Link>
              </Button>
              <Button asChild>
                <Link href="/register">Register</Link>
              </Button>
            </>
          )}
          <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open navigation">
            <Menu className="h-5 w-5" aria-hidden="true" />
          </Button>
        </div>
      </div>
    </header>
  );
}
