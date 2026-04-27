"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function RegisterPage() {
  const router = useRouter();
  const { signUp } = useAuth();
  const [role, setRole] = useState<"student" | "pg_owner">("student");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    const formData = new FormData(event.currentTarget);
    try {
      const user = await signUp({
        full_name: String(formData.get("full_name")),
        email: String(formData.get("email")),
        phone: String(formData.get("phone") || ""),
        password: String(formData.get("password")),
        role,
      });
      router.push(user.role === "student" ? "/student/dashboard" : "/owner/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-220px)] max-w-2xl items-center px-4 py-16">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
          <CardDescription>Students receive 10 free credits. PG owners can submit listings for review.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4" onSubmit={onSubmit}>
            <div className="grid grid-cols-2 gap-3">
              <button type="button" onClick={() => setRole("student")} className={`rounded-md border p-3 text-sm font-medium ${role === "student" ? "border-stone-950 bg-stone-950 text-white" : "border-stone-200 bg-white text-stone-800"}`}>
                Student
              </button>
              <button type="button" onClick={() => setRole("pg_owner")} className={`rounded-md border p-3 text-sm font-medium ${role === "pg_owner" ? "border-stone-950 bg-stone-950 text-white" : "border-stone-200 bg-white text-stone-800"}`}>
                PG Owner
              </button>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="full_name">Full name</Label>
              <Input id="full_name" name="full_name" required minLength={2} />
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" name="email" type="email" required autoComplete="email" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="phone">Phone</Label>
                <Input id="phone" name="phone" type="tel" autoComplete="tel" />
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" name="password" type="password" minLength={8} required autoComplete="new-password" />
            </div>
            {error ? <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}
            <Button disabled={isSubmitting}>{isSubmitting ? "Creating account..." : "Create account"}</Button>
            <p className="text-xs leading-5 text-stone-500">
              Admin and super admin accounts are not publicly available and must be seeded or created directly in the database. TODO: move JWT storage to httpOnly cookies before production launch.
            </p>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
