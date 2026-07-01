"use client";

const sections = [
  "Intro",
  "Process",
  "Rewards",
  "Login",
];

interface ParallaxProgressProps {
  activeIndex: number;
  onNavigate: (index: number) => void;
}

export default function ParallaxProgress({
  activeIndex,
  onNavigate,
}: ParallaxProgressProps) {
  return (
    <div
      className="
        flex
        items-center
        gap-2
        rounded-full
        border
        border-white/70
        bg-white/65
        px-3
        py-2
        shadow-[0_12px_40px_rgba(15,118,110,0.13)]
        backdrop-blur-2xl
        dark:border-white/10
        dark:bg-slate-950/70
        dark:shadow-[0_12px_40px_rgba(0,0,0,0.35)]
      "
    >
      {sections.map((section, index) => (
        <button
          key={section}
          type="button"
          onClick={() => onNavigate(index)}
          className={`group flex cursor-pointer items-center gap-2 rounded-full px-2.5 py-2 transition ${
            activeIndex === index
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-500/25"
              : "text-emerald-900 hover:bg-white dark:text-emerald-100 dark:hover:bg-white/10"
          }`}
          aria-label={`Go to ${section}`}
        >
          <span
            className={`h-2.5 rounded-full transition-all ${
              activeIndex === index
                ? "w-6 bg-white"
                : "w-2.5 bg-emerald-700/30 group-hover:bg-emerald-600 dark:bg-emerald-300/35"
            }`}
          />

          <span className="hidden text-xs font-black sm:inline">
            {section}
          </span>
        </button>
      ))}
    </div>
  );
}