"use client";

import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import { useAuth } from "@/providers/AuthProvider";
import { AuthService } from "@/services/auth.service";

export type LoginVisualState =
  | "idle"
  | "email"
  | "password"
  | "loading"
  | "error"
  | "success";

interface LoginFormProps {
  onVisualStateChange?: (state: LoginVisualState) => void;
  onSwitchToRegister?: () => void;
}

export default function LoginForm({
  onVisualStateChange,
  onSwitchToRegister,
}: LoginFormProps) {
  const router = useRouter();
  const { refreshUser } = useAuth();

  const [formKey] = useState(() => Date.now().toString());

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setEmail("");
    setPassword("");
    setError("");
    onVisualStateChange?.("idle");
  }, [onVisualStateChange]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (loading) return;

    setLoading(true);
    setError("");
    onVisualStateChange?.("loading");

    try {
      await AuthService.login({
        email,
        password,
      });

      await refreshUser();

      onVisualStateChange?.("success");

      setTimeout(() => {
        router.replace("/welcome");
      }, 450);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Login failed. Please try again.",
      );

      onVisualStateChange?.("error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      key={formKey}
      onSubmit={handleSubmit}
      autoComplete="off"
      className="space-y-3.5"
    >
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm font-bold text-red-700">
          {error}
        </div>
      )}

      <div className="space-y-1.5">
        <label
          htmlFor="greensprint-email"
          className="block text-sm font-black text-slate-800"
        >
          Email Address
        </label>

        <input
          id="greensprint-email"
          name={`greensprint-email-${formKey}`}
          type="email"
          required
          autoComplete="off"
          data-lpignore="true"
          data-1p-ignore="true"
          value={email}
          onFocus={() => onVisualStateChange?.("email")}
          onBlur={() => onVisualStateChange?.("idle")}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="...@example.com"
          className="h-12 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
        />
      </div>

      <div className="space-y-1.5">
        <label
          htmlFor="greensprint-password"
          className="block text-sm font-black text-slate-800"
        >
          Password
        </label>

        <div className="relative">
          <input
            id="greensprint-password"
            name={`greensprint-password-${formKey}`}
            type={showPassword ? "text" : "password"}
            required
            autoComplete="new-password"
            data-lpignore="true"
            data-1p-ignore="true"
            value={password}
            onFocus={() => onVisualStateChange?.("password")}
            onBlur={() => onVisualStateChange?.("idle")}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter password"
            className="h-12 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 pr-12 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
          />

          <button
            type="button"
            onClick={() => setShowPassword((current) => !current)}
            className="absolute right-2 top-1/2 grid h-9 w-9 -translate-y-1/2 cursor-pointer place-items-center rounded-xl text-emerald-700 transition hover:bg-emerald-50 hover:text-emerald-900"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? (
              <EyeOff className="h-[18px] w-[18px]" />
            ) : (
              <Eye className="h-[18px] w-[18px]" />
            )}
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between gap-4 pt-1">
        <label className="flex cursor-pointer items-center gap-2.5 text-sm font-bold text-slate-600">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={() => setRememberMe((current) => !current)}
            className="h-[18px] w-[18px] cursor-pointer rounded-md accent-emerald-500"
          />
          Remember
        </label>

        <button
          type="button"
          onClick={() => alert("Forgot password flow will be added later.")}
          className="cursor-pointer text-sm font-black text-emerald-700 transition hover:text-emerald-900 hover:underline hover:underline-offset-4"
        >
          Forgot password?
        </button>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="group relative mt-1 flex h-12 w-full cursor-pointer items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-600 via-green-500 to-lime-400 text-sm font-black text-white shadow-[0_16px_38px_rgba(16,185,129,0.34)] transition hover:-translate-y-1 hover:shadow-[0_22px_52px_rgba(16,185,129,0.48)] active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-70"
      >
        <span className="absolute inset-0 translate-x-[-120%] bg-gradient-to-r from-transparent via-white/35 to-transparent transition-transform duration-700 group-hover:translate-x-[120%]" />

        {loading ? (
          <span className="relative flex items-center gap-3">
            <span className="h-[18px] w-[18px] animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Signing in
          </span>
        ) : (
          <span className="relative">
            Continue{" "}
            <span className="inline-block transition group-hover:translate-x-1">
              →
            </span>
          </span>
        )}
      </button>

      <div className="pt-1 text-center">
        <p className="text-sm font-semibold text-slate-500">
          New to GreenSprint?
        </p>

        <button
          type="button"
          onClick={onSwitchToRegister}
          className="mt-0.5 inline-flex cursor-pointer text-sm font-black text-emerald-700 transition hover:text-emerald-900 hover:underline hover:underline-offset-4"
        >
          Create Account
        </button>
      </div>
    </form>
  );
}
