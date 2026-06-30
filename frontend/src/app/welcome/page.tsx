"use client";

import { useRouter } from "next/navigation";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import WelcomeExperience from "@/components/welcome/WelcomeExperience";

export default function WelcomePage() {
  const router = useRouter();

  return (
    <ProtectedRoute
      allowedRoles={[
        "USER",
        "ORGANIZATION",
        "ADMIN",
      ]}
    >
      <WelcomeExperience
        onContinue={() =>
          router.replace("/dashboard")
        }
      />
    </ProtectedRoute>
  );
}