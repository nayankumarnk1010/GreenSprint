"use client";

import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/providers/ThemeProvider";

export default function ThemeToggle() {
  const { theme, mounted, toggleTheme } = useTheme();

  const isDark = mounted && theme === "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="
        pointer-events-auto
        flex
        h-11
        cursor-pointer
        items-center
        gap-2
        rounded-full
        border
        border-white/80
        bg-white/75
        px-3
        text-sm
        font-black
        text-emerald-950
        shadow-[0_12px_40px_rgba(15,118,110,0.14)]
        backdrop-blur-2xl
        transition
        hover:-translate-y-0.5
        hover:bg-white
        dark:border-white/10
        dark:bg-slate-950/70
        dark:text-emerald-100
        dark:shadow-[0_12px_40px_rgba(0,0,0,0.35)]
        dark:hover:bg-slate-900
      "
      aria-label="Toggle theme"
    >
      <span
        className="
          grid
          h-7
          w-7
          place-items-center
          rounded-full
          bg-gradient-to-br
          from-emerald-600
          to-lime-400
          text-white
          shadow-lg
        "
      >
        {isDark ? (
          <Moon className="h-4 w-4" />
        ) : (
          <Sun className="h-4 w-4" />
        )}
      </span>

      <span className="hidden sm:inline">
        {isDark ? "Dark" : "Light"}
      </span>
    </button>
  );
}