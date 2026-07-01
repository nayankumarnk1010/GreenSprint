"use client";

import type { FormEvent } from "react";
import { useEffect, useId, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import { AuthService } from "@/services/auth.service";

export type RegisterVisualState =
  | "idle"
  | "name"
  | "email"
  | "role"
  | "password"
  | "confirm"
  | "loading"
  | "error"
  | "success";

interface RegisterFormProps {
  onVisualStateChange?: (state: RegisterVisualState) => void;
  onSwitchToLogin?: () => void;
}

type RegisterRole = "USER" | "ORGANIZATION";

export default function RegisterForm({
  onVisualStateChange,
  onSwitchToLogin,
}: RegisterFormProps) {
  const formId = useId().replace(/:/g, "");

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<RegisterRole>("USER");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setFullName("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setRole("USER");
    setError("");
    onVisualStateChange?.("idle");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (loading) return;

    const cleanName = fullName.trim();
    const cleanEmail = email.trim();

    if (!cleanName) {
      setError("Please enter your full name.");
      onVisualStateChange?.("error");
      return;
    }

    if (!cleanEmail) {
      setError("Please enter your email address.");
      onVisualStateChange?.("error");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      onVisualStateChange?.("error");
      return;
    }

    if (password !== confirmPassword) {
      setError("Password and confirm password do not match.");
      onVisualStateChange?.("error");
      return;
    }

    setLoading(true);
    setError("");
    onVisualStateChange?.("loading");

    try {
      await AuthService.register({
        full_name: cleanName,
        email: cleanEmail,
        password,
        role,
      });

      onVisualStateChange?.("success");

      setTimeout(() => {
        onSwitchToLogin?.();
      }, 700);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Registration failed. Please try again."
      );

      onVisualStateChange?.("error");
    } finally {
      setLoading(false);
    }
  }

  function selectRole(nextRole: RegisterRole) {
    setRole(nextRole);
    onVisualStateChange?.("role");
  }

  return (
    <form
      key={formId}
      onSubmit={handleSubmit}
      autoComplete="off"
      className="space-y-3"
    >
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-3.5 py-2 text-sm font-bold text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1">
          <label
            htmlFor="greensprint-register-name"
            className="block text-sm font-black text-slate-800"
          >
            Full Name
          </label>

          <input
            id="greensprint-register-name"
            name={`greensprint-register-name-${formId}`}
            type="text"
            required
            autoComplete="off"
            data-lpignore="true"
            data-1p-ignore="true"
            value={fullName}
            onFocus={() => onVisualStateChange?.("name")}
            onBlur={() => onVisualStateChange?.("idle")}
            onChange={(event) =>
              setFullName(event.target.value)
            }
            placeholder="Enter your name"
            className="h-10 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
          />
        </div>

        <div className="space-y-1">
          <label
            htmlFor="greensprint-register-email"
            className="block text-sm font-black text-slate-800"
          >
            Email Address
          </label>

          <input
            id="greensprint-register-email"
            name={`greensprint-register-email-${formId}`}
            type="email"
            required
            autoComplete="off"
            data-lpignore="true"
            data-1p-ignore="true"
            value={email}
            onFocus={() => onVisualStateChange?.("email")}
            onBlur={() => onVisualStateChange?.("idle")}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            placeholder="user@example.com"
            className="h-10 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
          />
        </div>
      </div>

      <div className="space-y-1">
        <label className="block text-sm font-black text-slate-800">
          Account Type
        </label>

        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => selectRole("USER")}
            className={`h-10 cursor-pointer rounded-2xl border text-sm font-black transition ${
              role === "USER"
                ? "border-emerald-500 bg-emerald-600 text-white shadow-lg shadow-emerald-500/20"
                : "border-emerald-100 bg-white/90 text-slate-600 hover:border-emerald-300 hover:bg-white"
            }`}
          >
            User
          </button>

          <button
            type="button"
            onClick={() => selectRole("ORGANIZATION")}
            className={`h-10 cursor-pointer rounded-2xl border text-sm font-black transition ${
              role === "ORGANIZATION"
                ? "border-emerald-500 bg-emerald-600 text-white shadow-lg shadow-emerald-500/20"
                : "border-emerald-100 bg-white/90 text-slate-600 hover:border-emerald-300 hover:bg-white"
            }`}
          >
            Organization
          </button>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1">
          <label
            htmlFor="greensprint-register-password"
            className="block text-sm font-black text-slate-800"
          >
            Password
          </label>

          <div className="relative">
            <input
              id="greensprint-register-password"
              name={`greensprint-register-password-${formId}`}
              type={showPassword ? "text" : "password"}
              required
              autoComplete="new-password"
              data-lpignore="true"
              data-1p-ignore="true"
              value={password}
              onFocus={() =>
                onVisualStateChange?.("password")
              }
              onBlur={() =>
                onVisualStateChange?.("idle")
              }
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Min. 8 characters"
              className="h-10 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 pr-11 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword((current) => !current)
              }
              className="absolute right-2 top-1/2 grid h-8 w-8 -translate-y-1/2 cursor-pointer place-items-center rounded-xl text-emerald-700 transition hover:bg-emerald-50 hover:text-emerald-900"
              aria-label={
                showPassword
                  ? "Hide password"
                  : "Show password"
              }
            >
              {showPassword ? (
                <EyeOff className="h-[17px] w-[17px]" />
              ) : (
                <Eye className="h-[17px] w-[17px]" />
              )}
            </button>
          </div>
        </div>

        <div className="space-y-1">
          <label
            htmlFor="greensprint-register-confirm-password"
            className="block text-sm font-black text-slate-800"
          >
            Confirm
          </label>

          <div className="relative">
            <input
              id="greensprint-register-confirm-password"
              name={`greensprint-register-confirm-password-${formId}`}
              type={showConfirmPassword ? "text" : "password"}
              required
              autoComplete="new-password"
              data-lpignore="true"
              data-1p-ignore="true"
              value={confirmPassword}
              onFocus={() =>
                onVisualStateChange?.("confirm")
              }
              onBlur={() =>
                onVisualStateChange?.("idle")
              }
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
              placeholder="Re-enter password"
              className="h-10 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 pr-11 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
            />

            <button
              type="button"
              onClick={() =>
                setShowConfirmPassword((current) => !current)
              }
              className="absolute right-2 top-1/2 grid h-8 w-8 -translate-y-1/2 cursor-pointer place-items-center rounded-xl text-emerald-700 transition hover:bg-emerald-50 hover:text-emerald-900"
              aria-label={
                showConfirmPassword
                  ? "Hide confirm password"
                  : "Show confirm password"
              }
            >
              {showConfirmPassword ? (
                <EyeOff className="h-[17px] w-[17px]" />
              ) : (
                <Eye className="h-[17px] w-[17px]" />
              )}
            </button>
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="group relative mt-1 flex h-11 w-full cursor-pointer items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-600 via-green-500 to-lime-400 text-sm font-black text-white shadow-[0_16px_38px_rgba(16,185,129,0.34)] transition hover:-translate-y-1 hover:shadow-[0_22px_52px_rgba(16,185,129,0.48)] active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-70"
      >
        <span className="absolute inset-0 translate-x-[-120%] bg-gradient-to-r from-transparent via-white/35 to-transparent transition-transform duration-700 group-hover:translate-x-[120%]" />

        {loading ? (
          <span className="relative flex items-center gap-3">
            <span className="h-[17px] w-[17px] animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Creating account
          </span>
        ) : (
          <span className="relative">
            Create Account{" "}
            <span className="inline-block transition group-hover:translate-x-1">
              →
            </span>
          </span>
        )}
      </button>

      <div className="pt-0.5 text-center">
        <span className="text-sm font-semibold text-slate-500">
          Already have an account?{" "}
        </span>

        <button
          type="button"
          onClick={onSwitchToLogin}
          className="cursor-pointer text-sm font-black text-emerald-700 transition hover:text-emerald-900 hover:underline hover:underline-offset-4"
        >
          Login
        </button>
      </div>
    </form>
  );
}