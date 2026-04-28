"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { apiRequest, clearStoredToken, getStoredToken, login, register, setStoredToken, startLoginOtp, verifyLoginOtp } from "@/lib/api-client";
import type { LoginOtpStartResponse } from "@/lib/types";
import type { AuthUser, UserRole } from "@/lib/types";

type AuthContextValue = {
  user: AuthUser | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<AuthUser>;
  startOtpSignIn: (email: string, password: string) => Promise<LoginOtpStartResponse>;
  verifyOtpSignIn: (challengeId: string, otp: string) => Promise<AuthUser>;
  signUp: (input: {
    full_name: string;
    email: string;
    phone?: string;
    password: string;
    role: "student" | "pg_owner";
  }) => Promise<AuthUser>;
  signOut: () => void;
  hasRole: (roles: UserRole[]) => boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    function expireSession() {
      clearStoredToken();
      setUser(null);
    }
    window.addEventListener("campusstay:session-expired", expireSession);
    async function loadCurrentUser() {
      const token = getStoredToken();
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const currentUser = await apiRequest<AuthUser>("/api/v1/auth/me");
        setUser(currentUser);
      } catch {
        clearStoredToken();
      } finally {
        setIsLoading(false);
      }
    }
    loadCurrentUser();
    return () => window.removeEventListener("campusstay:session-expired", expireSession);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      signIn: async (email, password) => {
        const response = await login(email, password);
        setStoredToken(response.access_token);
        setUser(response.user);
        return response.user;
      },
      startOtpSignIn: (email, password) => startLoginOtp(email, password),
      verifyOtpSignIn: async (challengeId, otp) => {
        const response = await verifyLoginOtp(challengeId, otp);
        setStoredToken(response.access_token);
        setUser(response.user);
        return response.user;
      },
      signUp: async (input) => {
        const response = await register(input);
        setStoredToken(response.access_token);
        setUser(response.user);
        return response.user;
      },
      signOut: () => {
        clearStoredToken();
        setUser(null);
      },
      hasRole: (roles) => Boolean(user && roles.includes(user.role)),
    }),
    [isLoading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
