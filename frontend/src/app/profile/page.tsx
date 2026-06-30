"use client";

import { useRouter } from "next/navigation";

import LivingTreeBackground from "@/components/background/LivingTreeBackground";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/providers/AuthProvider";

function ProfileContent() {
  const router = useRouter();

  const {
    user,
    logout,
  } = useAuth();

  return (
    <main className="relative min-h-screen overflow-hidden">
      <LivingTreeBackground />

      <div
        className="
          relative
          z-10
          min-h-screen
          px-6
          py-8
          text-white
          lg:px-16
        "
      >
        <header
          className="
            mx-auto
            flex
            max-w-6xl
            items-center
            justify-between
          "
        >
          <div>
            <p
              className="
                text-xs
                uppercase
                tracking-[0.35em]
                text-emerald-300
              "
            >
              GreenSprint
            </p>

            <h1
              className="
                mt-3
                text-4xl
                font-black
                tracking-tight
                text-white
                md:text-5xl
              "
            >
              Profile
            </h1>
          </div>

          <button
            type="button"
            onClick={() =>
              router.push("/dashboard")
            }
            className="
              rounded-2xl
              border
              border-white/10
              bg-white/5
              px-5
              py-3
              text-sm
              font-medium
              text-slate-200
              backdrop-blur-xl
              transition-all
              hover:border-emerald-400/40
              hover:bg-emerald-400/10
              hover:text-emerald-200
            "
          >
            Back to Dashboard
          </button>
        </header>

        <section
          className="
            mx-auto
            mt-12
            grid
            max-w-6xl
            gap-8
            lg:grid-cols-[0.8fr_1.2fr]
          "
        >
          <div
            className="
              rounded-[2rem]
              border
              border-white/10
              bg-white/5
              p-8
              shadow-2xl
              shadow-emerald-500/10
              backdrop-blur-2xl
            "
          >
            <div
              className="
                flex
                h-24
                w-24
                items-center
                justify-center
                rounded-3xl
                bg-gradient-to-br
                from-emerald-400
                to-emerald-700
                text-4xl
                font-black
                text-white
                shadow-xl
                shadow-emerald-500/30
              "
            >
              {user?.full_name
                ?.charAt(0)
                ?.toUpperCase() || "G"}
            </div>

            <h2
              className="
                mt-6
                text-3xl
                font-black
                text-white
              "
            >
              {user?.full_name}
            </h2>

            <p
              className="
                mt-2
                text-slate-400
              "
            >
              {user?.email}
            </p>

            <div
              className="
                mt-6
                inline-flex
                rounded-full
                border
                border-emerald-400/30
                bg-emerald-400/10
                px-4
                py-2
                text-sm
                font-semibold
                text-emerald-300
              "
            >
              {user?.role}
            </div>

            <button
              type="button"
              onClick={logout}
              className="
                mt-8
                h-12
                w-full
                rounded-2xl
                border
                border-red-400/30
                bg-red-500/10
                font-semibold
                text-red-200
                transition-all
                hover:bg-red-500/20
              "
            >
              Logout
            </button>
          </div>

          <div
            className="
              rounded-[2rem]
              border
              border-white/10
              bg-black/30
              p-8
              shadow-2xl
              shadow-black/30
              backdrop-blur-2xl
            "
          >
            <p
              className="
                text-xs
                uppercase
                tracking-[0.3em]
                text-emerald-300
              "
            >
              Account Details
            </p>

            <div
              className="
                mt-8
                grid
                gap-5
              "
            >
              <ProfileRow
                label="User ID"
                value={user?.id || "-"}
              />

              <ProfileRow
                label="Full Name"
                value={user?.full_name || "-"}
              />

              <ProfileRow
                label="Email"
                value={user?.email || "-"}
              />

              <ProfileRow
                label="Role"
                value={user?.role || "-"}
              />
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function ProfileRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div
      className="
        rounded-2xl
        border
        border-white/10
        bg-white/5
        p-5
      "
    >
      <p
        className="
          text-xs
          uppercase
          tracking-[0.25em]
          text-slate-500
        "
      >
        {label}
      </p>

      <p
        className="
          mt-2
          break-all
          text-base
          font-medium
          text-slate-100
        "
      >
        {value}
      </p>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute
      allowedRoles={[
        "USER",
        "ORGANIZATION",
        "ADMIN",
      ]}
    >
      <ProfileContent />
    </ProtectedRoute>
  );
}