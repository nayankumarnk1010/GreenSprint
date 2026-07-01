"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

type ThemeMode = "light" | "dark";

interface ThemeContextType {
  theme: ThemeMode;
  mounted: boolean;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
}

const ThemeContext =
  createContext<ThemeContextType | null>(null);

const STORAGE_KEY = "greensprint-theme";

export function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [theme, setThemeState] =
    useState<ThemeMode>("light");

  const [mounted, setMounted] = useState(false);

  function applyTheme(nextTheme: ThemeMode) {
    const root = document.documentElement;

    root.classList.toggle("dark", nextTheme === "dark");
    root.dataset.theme = nextTheme;
  }

  function setTheme(nextTheme: ThemeMode) {
    setThemeState(nextTheme);
    localStorage.setItem(STORAGE_KEY, nextTheme);
    applyTheme(nextTheme);
  }

  function toggleTheme() {
    setTheme(theme === "light" ? "dark" : "light");
  }

  useEffect(() => {
    const savedTheme =
      localStorage.getItem(STORAGE_KEY) as ThemeMode | null;

    const nextTheme =
      savedTheme === "dark" || savedTheme === "light"
        ? savedTheme
        : "light";

    setThemeState(nextTheme);
    applyTheme(nextTheme);
    setMounted(true);
  }, []);

  return (
    <ThemeContext.Provider
      value={{
        theme,
        mounted,
        toggleTheme,
        setTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error(
      "useTheme must be used within ThemeProvider"
    );
  }

  return context;
}