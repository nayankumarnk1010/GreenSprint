"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/providers/AuthProvider";
import type { UserRole } from "@/types/auth";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export default function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const router = useRouter();

  const {
    user,
    loading,
    isAuthenticated,
  } = useAuth();

  useEffect(() => {
    if (loading) return;

    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    if (
      allowedRoles &&
      user &&
      !allowedRoles.includes(user.role)
    ) {
      router.replace("/dashboard");
    }
  }, [
    loading,
    isAuthenticated,
    user,
    router,
    allowedRoles,
  ]);

  if (loading) {
    return (
      <main
        className="
          flex
          min-h-screen
          items-center
          justify-center
          bg-slate-950
          text-white
        "
      >
        <div
          className="
            rounded-3xl
            border
            border-white/10
            bg-white/5
            px-8
            py-6
            text-center
            shadow-2xl
            shadow-emerald-500/10
            backdrop-blur-xl
          "
        >
          <div
            className="
              mx-auto
              mb-4
              h-10
              w-10
              animate-spin
              rounded-full
              border-2
              border-emerald-400/20
              border-t-emerald-300
            "
          />

          <p
            className="
              text-sm
              uppercase
              tracking-[0.3em]
              text-emerald-300
            "
          >
            Loading GreenSprint
          </p>
        </div>
      </main>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (
    allowedRoles &&
    user &&
    !allowedRoles.includes(user.role)
  ) {
    return null;
  }

  return <>{children}</>;
}