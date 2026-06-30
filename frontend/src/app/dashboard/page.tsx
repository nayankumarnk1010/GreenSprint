"use client";

import { useRouter } from "next/navigation";

import LivingTreeBackground from "@/components/background/LivingTreeBackground";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/providers/AuthProvider";

function DashboardContent() {
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
            max-w-7xl
            flex-col
            gap-6
            md:flex-row
            md:items-center
            md:justify-between
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
              GreenSprint Dashboard
            </p>

            <h1
              className="
                mt-3
                text-4xl
                font-black
                tracking-tight
                text-white
                md:text-6xl
              "
            >
              Welcome,
              <br />
              {user?.full_name || "Eco Champion"}.
            </h1>

            <p
              className="
                mt-4
                max-w-2xl
                text-lg
                leading-relaxed
                text-slate-300
              "
            >
              Track verified sustainability actions,
              environmental impact, campaigns, AI
              insights, and community progress from
              one intelligent dashboard.
            </p>
          </div>

          <div
            className="
              flex
              flex-wrap
              gap-3
            "
          >
            <button
              type="button"
              onClick={() =>
                router.push("/profile")
              }
              className="
                rounded-2xl
                border
                border-white/10
                bg-white/5
                px-5
                py-3
                text-sm
                font-semibold
                text-slate-200
                backdrop-blur-xl
                transition-all
                hover:border-emerald-400/40
                hover:bg-emerald-400/10
                hover:text-emerald-200
              "
            >
              Profile
            </button>

            <button
              type="button"
              onClick={logout}
              className="
                rounded-2xl
                border
                border-red-400/30
                bg-red-500/10
                px-5
                py-3
                text-sm
                font-semibold
                text-red-200
                backdrop-blur-xl
                transition-all
                hover:bg-red-500/20
              "
            >
              Logout
            </button>
          </div>
        </header>

        <section
          className="
            mx-auto
            mt-12
            grid
            max-w-7xl
            gap-6
            md:grid-cols-3
          "
        >
          <DashboardStat
            title="Role"
            value={user?.role || "-"}
            subtitle="Current access level"
          />

          <DashboardStat
            title="AI Modules"
            value="16"
            subtitle="Backend modules complete"
          />

          <DashboardStat
            title="System"
            value="Ready"
            subtitle="Connected to FastAPI backend"
          />
        </section>

        <section
          className="
            mx-auto
            mt-8
            grid
            max-w-7xl
            gap-6
            lg:grid-cols-3
          "
        >
          <DashboardCard
            title="User Workspace"
            description="Submit green actions, upload proof, view AI verification, impact, rewards, and plant health guidance."
            action="Open User Tools"
            onClick={() =>
              alert("User module pages will be added next.")
            }
          />

          <DashboardCard
            title="Organization Workspace"
            description="Create sustainability campaigns, manage members, link challenges, and generate ESG reports."
            action="Open Organization Tools"
            onClick={() =>
              alert("Organization module pages will be added next.")
            }
          />

          <DashboardCard
            title="Admin Workspace"
            description="Moderate users, submissions, organizations, platform settings, AI reviews, and system health."
            action="Open Admin Tools"
            onClick={() =>
              alert("Admin module pages will be added next.")
            }
          />
        </section>
      </div>
    </main>
  );
}

function DashboardStat({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div
      className="
        rounded-[2rem]
        border
        border-white/10
        bg-white/5
        p-6
        shadow-2xl
        shadow-emerald-500/10
        backdrop-blur-2xl
      "
    >
      <p
        className="
          text-xs
          uppercase
          tracking-[0.25em]
          text-slate-400
        "
      >
        {title}
      </p>

      <h2
        className="
          mt-4
          text-4xl
          font-black
          text-emerald-300
        "
      >
        {value}
      </h2>

      <p
        className="
          mt-2
          text-sm
          text-slate-400
        "
      >
        {subtitle}
      </p>
    </div>
  );
}

function DashboardCard({
  title,
  description,
  action,
  onClick,
}: {
  title: string;
  description: string;
  action: string;
  onClick: () => void;
}) {
  return (
    <div
      className="
        rounded-[2rem]
        border
        border-white/10
        bg-black/30
        p-7
        shadow-2xl
        shadow-black/30
        backdrop-blur-2xl
        transition-all
        hover:-translate-y-1
        hover:border-emerald-400/40
        hover:bg-emerald-400/10
      "
    >
      <h3
        className="
          text-2xl
          font-black
          text-white
        "
      >
        {title}
      </h3>

      <p
        className="
          mt-4
          min-h-24
          text-sm
          leading-relaxed
          text-slate-300
        "
      >
        {description}
      </p>

      <button
        type="button"
        onClick={onClick}
        className="
          mt-6
          h-12
          w-full
          rounded-2xl
          bg-gradient-to-r
          from-emerald-500
          to-emerald-700
          font-semibold
          text-white
          shadow-xl
          shadow-emerald-500/20
          transition-all
          hover:scale-[1.02]
          hover:shadow-emerald-500/40
        "
      >
        {action}
      </button>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute
      allowedRoles={[
        "USER",
        "ORGANIZATION",
        "ADMIN",
      ]}
    >
      <DashboardContent />
    </ProtectedRoute>
  );
}