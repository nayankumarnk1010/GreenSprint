"use client";

import type { FormEvent } from "react";
import { useEffect, useId, useState } from "react";

import { AuthService } from "@/services/auth.service";

export type ForgotPasswordVisualState =
  | "idle"
  | "email"
  | "loading"
  | "error"
  | "success";

interface ForgotPasswordFormProps {
  onVisualStateChange?: (
    state: ForgotPasswordVisualState
  ) => void;
  onSwitchToLogin?: () => void;
}

export default function ForgotPasswordForm({
  onVisualStateChange,
  onSwitchToLogin,
}: ForgotPasswordFormProps) {
  const formId = useId().replace(/:/g, "");

  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setEmail("");
    setMessage("");
    setError("");
    onVisualStateChange?.("idle");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const cleanEmail = email.trim();

    if (!cleanEmail) {
      setError("Please enter your email address.");
      setMessage("");
      onVisualStateChange?.("error");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    onVisualStateChange?.("loading");

    try {
      const response =
        await AuthService.forgotPassword({
          email: cleanEmail,
        });

      setMessage(response.message);
      onVisualStateChange?.("success");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to process password reset request."
      );

      onVisualStateChange?.("error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      key={formId}
      onSubmit={handleSubmit}
      autoComplete="off"
      className="space-y-3.5"
    >
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm font-bold text-red-700 dark:border-red-400/20 dark:bg-red-500/10 dark:text-red-200">
          {error}
        </div>
      )}

      {message && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-3.5 py-2.5 text-sm font-bold text-emerald-800 dark:border-emerald-400/20 dark:bg-emerald-500/10 dark:text-emerald-200">
          {message}
        </div>
      )}

      <div className="space-y-1.5">
        <label
          htmlFor="greensprint-forgot-email"
          className="block text-sm font-black text-slate-800 dark:text-slate-100"
        >
          Email Address
        </label>

        <input
          id="greensprint-forgot-email"
          name={`greensprint-forgot-email-${formId}`}
          type="email"
          required
          autoComplete="off"
          data-lpignore="true"
          data-1p-ignore="true"
          value={email}
          onFocus={() =>
            onVisualStateChange?.("email")
          }
          onBlur={() =>
            onVisualStateChange?.("idle")
          }
          onChange={(event) =>
            setEmail(event.target.value)
          }
          placeholder="user@example.com"
          className="h-12 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100 dark:border-white/10 dark:bg-slate-950/70 dark:text-white dark:placeholder:text-slate-500 dark:hover:border-emerald-400/40 dark:focus:border-emerald-400 dark:focus:bg-slate-950 dark:focus:ring-emerald-400/10"
        />
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
            Sending instructions
          </span>
        ) : (
          <span className="relative">
            Send Reset Instructions →
          </span>
        )}
      </button>

      <div className="pt-1 text-center">
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="cursor-pointer text-sm font-black text-emerald-700 transition hover:text-emerald-900 hover:underline hover:underline-offset-4 dark:text-emerald-300 dark:hover:text-emerald-100"
        >
          Back to Login
        </button>
      </div>
    </form>
  );
}