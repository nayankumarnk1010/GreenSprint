"use client";

import { useTheme } from "@/providers/ThemeProvider";

interface LightForestPanoramaBackgroundProps {
  progress: number;
}

export default function LightForestPanoramaBackground({
  progress,
}: LightForestPanoramaBackgroundProps) {
  const { theme, mounted } = useTheme();

  const safeProgress = Math.min(1, Math.max(0, progress));
  const isDark = mounted && theme === "dark";

  return (
    <div
      className="
        pointer-events-none
        absolute
        inset-0
        overflow-hidden
        bg-emerald-50
        dark:bg-slate-950
      "
    >
      <div
        className="absolute inset-0 bg-cover bg-center will-change-[background-position]"
        style={{
          backgroundImage:
            "url('/assets/branding/light-forest-panorama.webp')",
          backgroundSize: "auto 108%",
          backgroundPosition: `${safeProgress * 100}% center`,
          filter: isDark
            ? "brightness(0.42) saturate(1.05) contrast(1.08)"
            : "brightness(1) saturate(1) contrast(1)",
        }}
      />

      {isDark ? (
        <>
          <div className="absolute inset-0 bg-gradient-to-r from-slate-950/88 via-emerald-950/45 to-slate-950/82" />
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950/45 via-transparent to-slate-950/92" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_72%_32%,rgba(16,185,129,0.22),transparent_32%),radial-gradient(circle_at_18%_20%,rgba(163,230,53,0.13),transparent_28%)]" />
        </>
      ) : (
        <>
          <div className="absolute inset-0 bg-gradient-to-r from-black/30 via-white/8 to-white/35" />
          <div className="absolute inset-0 bg-gradient-to-b from-white/10 via-transparent to-white/55" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.25),transparent_32%),radial-gradient(circle_at_80%_45%,rgba(255,255,255,0.5),transparent_34%)]" />
        </>
      )}

      <div
        className="
          absolute
          left-[-12%]
          top-[12%]
          h-[420px]
          w-[420px]
          rounded-full
          bg-lime-200/35
          blur-[90px]
          dark:bg-emerald-500/15
        "
        style={{
          transform: `translateX(${safeProgress * 220}px)`,
        }}
      />

      <div
        className="
          absolute
          right-[-10%]
          bottom-[8%]
          h-[460px]
          w-[460px]
          rounded-full
          bg-emerald-200/35
          blur-[100px]
          dark:bg-lime-400/10
        "
        style={{
          transform: `translateX(${safeProgress * -220}px)`,
        }}
      />
    </div>
  );
}