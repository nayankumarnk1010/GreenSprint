"use client";

import type { FormEvent } from "react";
import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Eye, EyeOff, Leaf, LockKeyhole, Sparkles } from "lucide-react";

import LightForestPanoramaBackground from "@/components/background/LightForestPanoramaBackground";
import ThemeToggle from "@/components/ui/ThemeToggle";
import { AuthService } from "@/services/auth.service";

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<ResetPasswordLoading />}>
      <ResetPasswordContent />
    </Suspense>
  );
}

function ResetPasswordLoading() {
  return (
    <main className="relative min-h-dvh overflow-hidden bg-emerald-50 text-slate-950 dark:bg-slate-950 dark:text-white">
      <LightForestPanoramaBackground progress={0.85} />

      <div className="relative z-10 flex min-h-dvh items-center justify-center px-5">
        <div className="rounded-3xl border border-white/80 bg-white/80 px-6 py-5 text-sm font-black text-emerald-800 shadow-xl backdrop-blur-2xl dark:border-white/10 dark:bg-slate-950/75 dark:text-emerald-200">
          Loading reset page...
        </div>
      </div>
    </main>
  );
}

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!token) {
      setError(
        "Reset token is missing. Please request a new password reset link."
      );
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Password and confirm password do not match.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response =
        await AuthService.resetPassword({
          token,
          new_password: password,
        });

      setSuccess(response.message);
      setPassword("");
      setConfirmPassword("");

      setTimeout(() => {
        window.location.href = "/login";
      }, 1200);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Password reset failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-dvh overflow-hidden bg-emerald-50 text-slate-950 dark:bg-slate-950 dark:text-white">
      <LightForestPanoramaBackground progress={0.85} />

      <header className="pointer-events-none absolute left-0 right-0 top-0 z-50 flex items-start justify-between gap-4 px-5 py-4 sm:px-8 lg:px-10">
        <button
          type="button"
          onClick={() => {
            window.location.href = "/login";
          }}
          className="pointer-events-auto flex cursor-pointer items-center gap-2 rounded-full border border-white/80 bg-white/75 px-4 py-2 text-sm font-black text-emerald-950 shadow-[0_12px_40px_rgba(15,118,110,0.14)] backdrop-blur-2xl transition hover:-translate-y-0.5 hover:bg-white dark:border-white/10 dark:bg-slate-950/70 dark:text-emerald-100 dark:shadow-black/30 dark:hover:bg-slate-900"
        >
          <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-emerald-600 to-lime-400 text-white shadow-lg">
            <Leaf className="h-4 w-4" />
          </span>
          GreenSprint
        </button>

        <div className="pointer-events-auto">
          <ThemeToggle />
        </div>
      </header>

      <section className="relative z-20 flex min-h-dvh items-center justify-center px-5 pb-8 pt-28 sm:px-8">
        <div className="mx-auto grid w-full max-w-6xl items-center gap-8 lg:grid-cols-[0.95fr_0.9fr]">
          <div className="hidden rounded-[1.9rem] border border-white/80 bg-white/62 p-7 shadow-[0_24px_70px_rgba(15,118,110,0.12)] backdrop-blur-2xl dark:border-white/10 dark:bg-slate-950/68 dark:shadow-black/30 lg:block">
            <p className="text-xs font-black uppercase tracking-[0.26em] text-emerald-700 dark:text-emerald-300">
              Password Recovery
            </p>

            <h1 className="mt-4 max-w-xl text-4xl font-black leading-[0.94] tracking-[-0.055em] text-slate-950 dark:text-white xl:text-5xl">
              Create a new secure password.
            </h1>

            <p className="mt-4 max-w-md text-sm font-semibold leading-7 text-slate-600 dark:text-slate-300 xl:text-base">
              Your GreenSprint account protects your eco missions,
              verified submissions, rewards, badges, and impact
              records.
            </p>
          </div>

          <div className="relative mx-auto w-full max-w-[430px] overflow-hidden rounded-[2rem] border border-white/90 bg-white/88 p-5 shadow-[0_28px_80px_rgba(15,118,110,0.18)] backdrop-blur-2xl transition-all duration-300 dark:border-white/10 dark:bg-slate-950/75 dark:shadow-black/30 sm:p-6">
            <div className="pointer-events-none absolute -right-20 -top-20 h-40 w-40 rounded-full bg-emerald-200/50 blur-3xl dark:bg-emerald-500/15" />
            <div className="pointer-events-none absolute -bottom-24 left-8 h-44 w-44 rounded-full bg-lime-200/35 blur-3xl dark:bg-lime-400/10" />

            <div className="relative">
              <div className="mb-5 flex items-start justify-between gap-4">
                <div>
                  <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-600 to-lime-400 text-white shadow-[0_14px_34px_rgba(16,185,129,0.35)]">
                    <LockKeyhole className="h-5 w-5" />
                  </div>

                  <p className="text-[0.65rem] font-black uppercase tracking-[0.24em] text-emerald-700 dark:text-emerald-300">
                    GreenSprint Security
                  </p>

                  <h2 className="mt-2 text-[1.7rem] font-black leading-none tracking-[-0.045em] text-slate-950 dark:text-white">
                    Reset password
                  </h2>
                </div>

                <span className="mt-1 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1 text-[0.65rem] font-black uppercase tracking-[0.16em] text-emerald-700 dark:border-emerald-400/20 dark:bg-emerald-400/10 dark:text-emerald-200">
                  Secure
                </span>
              </div>

              <p className="-mt-2 mb-5 text-sm font-semibold leading-6 text-slate-500 dark:text-slate-300">
                Enter a strong new password to regain access to your
                account.
              </p>

              {!token && (
                <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm font-bold text-red-700 dark:border-red-400/20 dark:bg-red-500/10 dark:text-red-200">
                  Reset token is missing. Please request a new password reset link.
                </div>
              )}

              {error && (
                <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm font-bold text-red-700 dark:border-red-400/20 dark:bg-red-500/10 dark:text-red-200">
                  {error}
                </div>
              )}

              {success && (
                <div className="mb-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-3.5 py-2.5 text-sm font-bold text-emerald-800 dark:border-emerald-400/20 dark:bg-emerald-500/10 dark:text-emerald-200">
                  {success}
                </div>
              )}

              <form
                onSubmit={handleSubmit}
                autoComplete="off"
                className="space-y-3.5"
              >
                <PasswordInput
                  id="greensprint-new-password"
                  label="New Password"
                  value={password}
                  show={showPassword}
                  placeholder="Newpass@123"
                  onToggle={() =>
                    setShowPassword((current) => !current)
                  }
                  onChange={setPassword}
                />

                <PasswordInput
                  id="greensprint-confirm-new-password"
                  label="Confirm Password"
                  value={confirmPassword}
                  show={showConfirmPassword}
                  placeholder="Re-enter password"
                  onToggle={() =>
                    setShowConfirmPassword(
                      (current) => !current
                    )
                  }
                  onChange={setConfirmPassword}
                />

                <p className="text-xs font-bold leading-5 text-slate-500 dark:text-slate-400">
                  Password must include uppercase, lowercase, number,
                  and special character.
                </p>

                <button
                  type="submit"
                  disabled={loading || !token}
                  className="group relative mt-1 flex h-12 w-full cursor-pointer items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-600 via-green-500 to-lime-400 text-sm font-black text-white shadow-[0_16px_38px_rgba(16,185,129,0.34)] transition hover:-translate-y-1 hover:shadow-[0_22px_52px_rgba(16,185,129,0.48)] active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  <span className="absolute inset-0 translate-x-[-120%] bg-gradient-to-r from-transparent via-white/35 to-transparent transition-transform duration-700 group-hover:translate-x-[120%]" />

                  {loading ? (
                    <span className="relative flex items-center gap-3">
                      <span className="h-[18px] w-[18px] animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Resetting password
                    </span>
                  ) : (
                    <span className="relative flex items-center gap-2">
                      <Sparkles className="h-4 w-4" />
                      Reset Password
                    </span>
                  )}
                </button>

                <div className="pt-1 text-center">
                  <button
                    type="button"
                    onClick={() => {
                      window.location.href = "/login";
                    }}
                    className="cursor-pointer text-sm font-black text-emerald-700 transition hover:text-emerald-900 hover:underline hover:underline-offset-4 dark:text-emerald-300 dark:hover:text-emerald-100"
                  >
                    Back to Login
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

function PasswordInput({
  id,
  label,
  value,
  show,
  placeholder,
  onToggle,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  show: boolean;
  placeholder: string;
  onToggle: () => void;
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-1.5">
      <label
        htmlFor={id}
        className="block text-sm font-black text-slate-800 dark:text-slate-100"
      >
        {label}
      </label>

      <div className="relative">
        <input
          id={id}
          name={id}
          type={show ? "text" : "password"}
          required
          autoComplete="new-password"
          data-lpignore="true"
          data-1p-ignore="true"
          value={value}
          onChange={(event) =>
            onChange(event.target.value)
          }
          placeholder={placeholder}
          className="h-12 w-full rounded-2xl border border-emerald-100 bg-white/94 px-4 pr-12 text-sm font-bold text-slate-900 shadow-inner outline-none backdrop-blur-xl transition placeholder:text-slate-400 hover:border-emerald-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100 dark:border-white/10 dark:bg-slate-950/70 dark:text-white dark:placeholder:text-slate-500 dark:hover:border-emerald-400/40 dark:focus:border-emerald-400 dark:focus:bg-slate-950 dark:focus:ring-emerald-400/10"
        />

        <button
          type="button"
          onClick={onToggle}
          className="absolute right-2 top-1/2 grid h-9 w-9 -translate-y-1/2 cursor-pointer place-items-center rounded-xl text-emerald-700 transition hover:bg-emerald-50 hover:text-emerald-900 dark:text-emerald-300 dark:hover:bg-white/10 dark:hover:text-emerald-100"
          aria-label={
            show ? "Hide password" : "Show password"
          }
        >
          {show ? (
            <EyeOff className="h-[18px] w-[18px]" />
          ) : (
            <Eye className="h-[18px] w-[18px]" />
          )}
        </button>
      </div>
    </div>
  );
}