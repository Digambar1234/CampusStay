"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const router = useRouter();
  const { startOtpSignIn, verifyOtpSignIn } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [challengeId, setChallengeId] = useState<string | null>(null);
  const [phoneHint, setPhoneHint] = useState<string | null>(null);
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    const formData = new FormData(event.currentTarget);
    try {
      const response = await startOtpSignIn(String(formData.get("email")), String(formData.get("password")));
      setChallengeId(response.challenge_id);
      setPhoneHint(response.phone_hint);
      setDevOtp(response.dev_otp ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function onVerifyOtp(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!challengeId) return;
    setError(null);
    setIsSubmitting(true);
    const formData = new FormData(event.currentTarget);
    try {
      const user = await verifyOtpSignIn(challengeId, String(formData.get("otp")));
      router.push(user.role === "student" ? "/student/dashboard" : user.role === "pg_owner" ? "/owner/dashboard" : "/admin/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "OTP verification failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-220px)] max-w-md items-center px-4 py-16">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>Use your CampusStay account to access protected dashboards.</CardDescription>
        </CardHeader>
        <CardContent>
          {!challengeId ? <form className="grid gap-4" onSubmit={onSubmit}>
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" required autoComplete="email" />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" name="password" type="password" required autoComplete="current-password" />
            </div>
            {error ? <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}
            <Button disabled={isSubmitting}>{isSubmitting ? "Sending OTP..." : "Continue"}</Button>
          </form> : (
            <form className="grid gap-4" onSubmit={onVerifyOtp}>
              <p className="text-sm text-stone-600">Enter the OTP sent to {phoneHint}.</p>
              {devOtp ? <p className="rounded-md bg-amber-50 p-3 text-sm text-amber-800">Development OTP: {devOtp}</p> : null}
              <div className="grid gap-2">
                <Label htmlFor="otp">OTP</Label>
                <Input id="otp" name="otp" inputMode="numeric" minLength={4} maxLength={10} required autoComplete="one-time-code" />
              </div>
              {error ? <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}
              <Button disabled={isSubmitting}>{isSubmitting ? "Verifying..." : "Verify and Login"}</Button>
              <Button type="button" variant="secondary" onClick={() => { setChallengeId(null); setPhoneHint(null); setDevOtp(null); setError(null); }}>
                Use another account
              </Button>
            </form>
          )}
          <p className="mt-4 text-sm text-stone-600">
            New here? <Link className="font-medium text-stone-950" href="/register">Create an account</Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
