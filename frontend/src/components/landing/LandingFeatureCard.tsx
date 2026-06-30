"use client";

import type { LucideIcon } from "lucide-react";

interface LandingFeatureCardProps {
  icon: LucideIcon;
  label: string;
  title: string;
  description: string;
}

export default function LandingFeatureCard({
  icon: Icon,
  label,
  title,
  description,
}: LandingFeatureCardProps) {
  return (
    <div className="group rounded-[1.7rem] border border-white/80 bg-white/74 p-5 shadow-[0_18px_55px_rgba(15,118,110,0.13)] backdrop-blur-2xl transition duration-300 hover:-translate-y-1.5 hover:border-emerald-200 hover:bg-white/90">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-emerald-500 to-lime-400 text-white shadow-lg transition group-hover:scale-105">
          <Icon className="h-6 w-6" />
        </div>

        <span className="rounded-full bg-emerald-50 px-3 py-1 text-[0.68rem] font-black uppercase tracking-[0.18em] text-emerald-700">
          {label}
        </span>
      </div>

      <h3 className="text-lg font-black tracking-[-0.03em] text-slate-950">
        {title}
      </h3>

      <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
        {description}
      </p>
    </div>
  );
}