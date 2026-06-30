"use client";

interface LightForestPanoramaBackgroundProps {
  progress: number;
}

export default function LightForestPanoramaBackground({
  progress,
}: LightForestPanoramaBackgroundProps) {
  const safeProgress = Math.min(1, Math.max(0, progress));

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden bg-emerald-50">
      <div
        className="absolute inset-0 bg-cover bg-center will-change-[background-position]"
        style={{
          backgroundImage:
            "url('/assets/branding/light-forest-panorama.webp')",
          backgroundSize: "auto 108%",
          backgroundPosition: `${safeProgress * 100}% center`,
        }}
      />

      <div className="absolute inset-0 bg-gradient-to-r from-black/30 via-white/8 to-white/35" />
      <div className="absolute inset-0 bg-gradient-to-b from-white/10 via-transparent to-white/55" />

      <div
        className="absolute left-[-12%] top-[12%] h-[420px] w-[420px] rounded-full bg-lime-200/35 blur-[90px]"
        style={{
          transform: `translateX(${safeProgress * 220}px)`,
        }}
      />

      <div
        className="absolute right-[-10%] bottom-[8%] h-[460px] w-[460px] rounded-full bg-emerald-200/35 blur-[100px]"
        style={{
          transform: `translateX(${safeProgress * -220}px)`,
        }}
      />

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.25),transparent_32%),radial-gradient(circle_at_80%_45%,rgba(255,255,255,0.5),transparent_34%)]" />
    </div>
  );
}