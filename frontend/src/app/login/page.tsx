"use client";

import { useEffect, useRef, useState } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";
import {
  BadgeCheck,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Leaf,
  Medal,
  ShieldCheck,
  Sparkles,
  Trophy,
  Upload,
  Users,
} from "lucide-react";

import LightForestPanoramaBackground from "@/components/background/LightForestPanoramaBackground";
import LoginForm, {
  type LoginVisualState,
} from "@/components/forms/LoginForm";
import LandingFeatureCard from "@/components/landing/LandingFeatureCard";
import ParallaxProgress from "@/components/landing/ParallaxProgress";
import RegisterForm, {
  type RegisterVisualState,
} from "@/components/forms/RegisterForm";
gsap.registerPlugin(ScrollTrigger, useGSAP);

const PANEL_COUNT = 4;

type AuthMode = "login" | "register";

type AuthVisualState =
  | LoginVisualState
  | RegisterVisualState;

export default function LoginPage() {
  const rootRef = useRef<HTMLElement | null>(null);
  const pinRef = useRef<HTMLElement | null>(null);
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const trackRef = useRef<HTMLDivElement | null>(null);

  const [progress, setProgress] = useState(0);
  const [authMode, setAuthMode] =
    useState<AuthMode>("login");

  const [visualState, setVisualState] =
    useState<AuthVisualState>("idle");

  const activeIndex = Math.min(
    PANEL_COUNT - 1,
    Math.round(progress * (PANEL_COUNT - 1))
  );

  useEffect(() => {
    const media = window.matchMedia("(min-width: 1024px)");

    if (!media.matches) return;

    const lenis = new Lenis({
      lerp: 0.08,
      smoothWheel: true,
    });

    let frameId = 0;

    function raf(time: number) {
      lenis.raf(time);
      frameId = requestAnimationFrame(raf);
    }

    frameId = requestAnimationFrame(raf);

    return () => {
      cancelAnimationFrame(frameId);
      lenis.destroy();
    };
  }, []);

  useGSAP(
    () => {
      const root = rootRef.current;
      const pin = pinRef.current;
      const track = trackRef.current;

      if (!root || !pin || !track) return;

      const media = gsap.matchMedia();

      media.add("(min-width: 1024px)", () => {
        const getDistance = () =>
          track.scrollWidth - window.innerWidth;

        const tween = gsap.to(track, {
          x: () => -getDistance(),
          ease: "none",
          scrollTrigger: {
            id: "greensprint-login-horizontal",
            trigger: root,
            pin,
            scrub: 0.85,
            start: "top top",
            end: () => `+=${getDistance()}`,
            invalidateOnRefresh: true,
            snap: {
              snapTo: 1 / (PANEL_COUNT - 1),
              duration: {
                min: 0.25,
                max: 0.55,
              },
              ease: "power2.out",
            },
            onUpdate: (self) => {
              setProgress(self.progress);
            },
          },
        });

        return () => {
          tween.kill();
        };
      });

      return () => {
        media.revert();
      };
    },
    {
      scope: rootRef,
    }
  );

  function handleMobileScroll() {
    const element = scrollerRef.current;

    if (!element) return;
    if (window.innerWidth >= 1024) return;

    const maxScroll =
      element.scrollWidth - element.clientWidth;

    const nextProgress =
      maxScroll <= 0 ? 0 : element.scrollLeft / maxScroll;

    setProgress(nextProgress);
  }

  function goToPanel(index: number) {
    if (window.innerWidth >= 1024) {
      const trigger = ScrollTrigger.getById(
        "greensprint-login-horizontal"
      );

      if (trigger) {
        const target =
          trigger.start +
          (trigger.end - trigger.start) *
            (index / (PANEL_COUNT - 1));

        window.scrollTo({
          top: target,
          behavior: "smooth",
        });
      }

      return;
    }

    const element = scrollerRef.current;

    if (!element) return;

    element.scrollTo({
      left: element.clientWidth * index,
      behavior: "smooth",
    });
  }

  return (
    <main
      ref={rootRef}
      className="relative bg-emerald-50 text-slate-950"
    >
      <section
        ref={pinRef}
        className="relative h-dvh overflow-hidden"
      >
        <LightForestPanoramaBackground progress={progress} />

        <header className="pointer-events-none absolute left-0 right-0 top-0 z-50 flex items-start justify-between gap-4 px-5 py-4 sm:px-8 lg:px-10">
          <button
            type="button"
            onClick={() => goToPanel(0)}
            className="pointer-events-auto flex cursor-pointer items-center gap-2 rounded-full border border-white/80 bg-white/75 px-4 py-2 text-sm font-black text-emerald-950 shadow-[0_12px_40px_rgba(15,118,110,0.14)] backdrop-blur-2xl transition hover:-translate-y-0.5 hover:bg-white"
          >
            <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-emerald-600 to-lime-400 text-white shadow-lg">
              <Leaf className="h-4 w-4" />
            </span>
            GreenSprint
          </button>

          <ParallaxProgress
            activeIndex={activeIndex}
            onNavigate={goToPanel}
          />
        </header>

        <div
          ref={scrollerRef}
          onScroll={handleMobileScroll}
          className="gs-horizontal-scroll relative z-20 h-dvh snap-x snap-mandatory overflow-x-auto overflow-y-hidden scroll-smooth lg:overflow-hidden"
        >
          <div
            ref={trackRef}
            className="flex h-dvh w-[400vw] will-change-transform"
          >
            <HeroPanel
              onExplore={() => goToPanel(1)}
              onLogin={() => goToPanel(3)}
            />

            <HowItWorksPanel onNext={() => goToPanel(2)} />

            <RewardsImpactPanel onNext={() => goToPanel(3)} />

            <LoginPanel
              authMode={authMode}
              visualState={visualState}
              onVisualStateChange={setVisualState}
              onAuthModeChange={(mode) => {
                setAuthMode(mode);
                setVisualState("idle");
              }}
            />
          </div>
        </div>

        <div className="pointer-events-none absolute bottom-4 left-1/2 z-40 -translate-x-1/2 rounded-full border border-white/80 bg-white/75 px-4 py-2 text-xs font-black text-emerald-900 shadow-lg backdrop-blur-xl lg:hidden">
          Swipe to explore
        </div>
      </section>
    </main>
  );
}

function HeroPanel({
  onExplore,
  onLogin,
}: {
  onExplore: () => void;
  onLogin: () => void;
}) {
  return (
    <section className="flex h-dvh w-screen shrink-0 snap-center items-center px-5 pb-14 pt-32 sm:px-8 lg:px-12 lg:pt-28">
      <div className="mx-auto grid w-full max-w-7xl items-center gap-10 lg:grid-cols-[0.95fr_0.85fr]">
        <div className="max-w-3xl">
          <p className="mb-5 inline-flex rounded-full border border-white/80 bg-white/72 px-4 py-2 text-[0.68rem] font-black uppercase tracking-[0.24em] text-emerald-800 shadow-lg backdrop-blur-2xl sm:text-xs">
            AI-Powered Sustainability Platform
          </p>

          <h1 className="max-w-3xl text-4xl font-black leading-[0.92] tracking-[-0.055em] text-white drop-shadow-[0_6px_22px_rgba(0,0,0,0.55)] sm:text-5xl md:text-6xl lg:text-7xl xl:text-[5.5rem]">
            Turn green actions into verified impact.
          </h1>

          <p className="mt-6 max-w-2xl text-sm font-bold leading-7 text-white drop-shadow-[0_3px_12px_rgba(0,0,0,0.45)] sm:text-base md:text-lg">
            GreenSprint helps users complete eco missions, upload proof, get AI
            verification, earn rewards, and track measurable environmental
            progress.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={onExplore}
              className="group h-13 cursor-pointer rounded-2xl bg-gradient-to-r from-emerald-600 via-green-500 to-lime-400 px-7 text-sm font-black text-white shadow-[0_18px_45px_rgba(16,185,129,0.38)] transition hover:-translate-y-1 hover:shadow-[0_24px_60px_rgba(16,185,129,0.52)] active:translate-y-0 sm:h-14 sm:text-base"
            >
              See How It Works{" "}
              <ChevronRight className="ml-1 inline h-5 w-5 transition group-hover:translate-x-1" />
            </button>

            <button
              type="button"
              onClick={onLogin}
              className="h-13 cursor-pointer rounded-2xl border border-white/85 bg-white/80 px-7 text-sm font-black text-emerald-950 shadow-lg backdrop-blur-2xl transition hover:-translate-y-1 hover:bg-white active:translate-y-0 sm:h-14 sm:text-base"
            >
              Login
            </button>
          </div>
        </div>

        <div className="hidden justify-end gap-4 lg:grid">
          <div className="ml-auto grid max-w-[520px] gap-4">
            <LandingFeatureCard
              icon={Sparkles}
              label="Platform"
              title="Eco missions"
              description="Users complete structured sustainability actions such as planting, recycling, saving water, and joining campaigns."
            />

            <LandingFeatureCard
              icon={ShieldCheck}
              label="AI"
              title="Proof verification"
              description="Uploaded action proof can be checked using AI-assisted verification before rewards are assigned."
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorksPanel({
  onNext,
}: {
  onNext: () => void;
}) {
  const steps = [
    {
      icon: CheckCircle2,
      title: "Choose a mission",
      text: "Users select an eco action from available challenges or campaigns.",
    },
    {
      icon: Upload,
      title: "Upload proof",
      text: "A photo or document is submitted as evidence of completion.",
    },
    {
      icon: ShieldCheck,
      title: "AI verification",
      text: "The system reviews proof quality, relevance, and possible fraud signals.",
    },
    {
      icon: Medal,
      title: "Earn rewards",
      text: "Verified actions contribute to XP, badges, ranking, and impact score.",
    },
  ];

  return (
    <section className="flex h-dvh w-screen shrink-0 snap-center items-center px-5 pb-14 pt-28 sm:px-8 lg:px-12">
      <div className="mx-auto grid w-full max-w-7xl items-center gap-8 lg:grid-cols-[0.82fr_1.18fr]">
        <div className="rounded-[2rem] border border-white/80 bg-white/75 p-6 shadow-[0_28px_80px_rgba(15,118,110,0.15)] backdrop-blur-2xl sm:p-8">
          <p className="text-sm font-black uppercase tracking-[0.28em] text-emerald-700">
            How It Works
          </p>

          <h2 className="mt-4 text-4xl font-black leading-[0.94] tracking-[-0.055em] text-slate-950 sm:text-5xl lg:text-6xl">
            From action to impact in four steps.
          </h2>

          <p className="mt-5 text-base font-semibold leading-7 text-slate-600">
            The platform is designed for users who want to
            take small sustainable actions and see meaningful,
            verified progress.
          </p>

          <button
            type="button"
            onClick={onNext}
            className="mt-7 h-14 cursor-pointer rounded-2xl bg-slate-950 px-7 text-base font-black text-white shadow-xl transition hover:-translate-y-1 hover:bg-emerald-800 active:translate-y-0"
          >
            View Rewards & Impact
          </button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {steps.map((step, index) => (
            <div
              key={step.title}
              className="rounded-[2rem] border border-white/80 bg-white/75 p-5 shadow-[0_22px_70px_rgba(15,118,110,0.14)] backdrop-blur-2xl transition hover:-translate-y-2 hover:bg-white/90"
            >
              <div className="mb-5 flex items-center justify-between">
                <div className="grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-emerald-600 to-lime-400 text-white shadow-lg">
                  <step.icon className="h-7 w-7" />
                </div>

                <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-black text-emerald-700">
                  Step {index + 1}
                </span>
              </div>

              <h3 className="text-xl font-black text-slate-950">
                {step.title}
              </h3>

              <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                {step.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function RewardsImpactPanel({
  onNext,
}: {
  onNext: () => void;
}) {
  return (
    <section className="flex h-dvh w-screen shrink-0 snap-center items-center px-5 pb-14 pt-28 sm:px-8 lg:px-12">
      <div className="mx-auto grid w-full max-w-7xl items-center gap-8 lg:grid-cols-[1fr_1fr]">
        <div className="grid gap-4 sm:grid-cols-2">
          <LandingFeatureCard
            icon={Trophy}
            label="Game"
            title="XP and levels"
            description="Verified actions can increase user progress through points, levels, streaks, and leaderboard rank."
          />

          <LandingFeatureCard
            icon={BadgeCheck}
            label="Rewards"
            title="Badges"
            description="Users unlock achievement badges for consistent and meaningful sustainability actions."
          />

          <LandingFeatureCard
            icon={BarChart3}
            label="Impact"
            title="Environmental metrics"
            description="The platform can estimate impact such as CO₂ saved, trees planted, waste reduced, or water saved."
          />

          <LandingFeatureCard
            icon={Users}
            label="Community"
            title="Campaigns"
            description="Organizations and communities can create campaigns and monitor participation through reports."
          />
        </div>

        <div className="rounded-[2rem] border border-white/80 bg-white/78 p-6 shadow-[0_28px_80px_rgba(15,118,110,0.16)] backdrop-blur-2xl sm:p-8">
          <p className="text-sm font-black uppercase tracking-[0.28em] text-emerald-700">
            Rewards + Impact
          </p>

          <h2 className="mt-4 text-4xl font-black leading-[0.94] tracking-[-0.055em] text-slate-950 sm:text-5xl lg:text-6xl">
            Make sustainability measurable and rewarding.
          </h2>

          <p className="mt-5 text-base font-semibold leading-7 text-slate-600">
            GreenSprint is not only about submitting actions.
            It creates a complete engagement loop through
            verification, progress, rewards, analytics, and
            community participation.
          </p>

          <button
            type="button"
            onClick={onNext}
            className="mt-7 h-14 cursor-pointer rounded-2xl bg-gradient-to-r from-emerald-600 via-green-500 to-lime-400 px-7 text-base font-black text-white shadow-[0_18px_45px_rgba(16,185,129,0.35)] transition hover:-translate-y-1 hover:shadow-[0_24px_60px_rgba(16,185,129,0.5)] active:translate-y-0"
          >
            Continue to Login
          </button>
        </div>
      </div>
    </section>
  );
}

function LoginPanel({
  authMode,
  visualState,
  onVisualStateChange,
  onAuthModeChange,
}: {
  authMode: AuthMode;
  visualState: AuthVisualState;
  onVisualStateChange: (state: AuthVisualState) => void;
  onAuthModeChange: (mode: AuthMode) => void;
}) {
  const copy =
    authMode === "login"
      ? getLoginCopy(visualState as LoginVisualState)
      : getRegisterCopy(visualState as RegisterVisualState);

  const stateClass =
    visualState === "error"
      ? "border-red-200 shadow-red-100"
      : visualState === "success"
        ? "border-lime-200 shadow-lime-100"
        : visualState === "loading"
          ? "border-emerald-300 shadow-emerald-200"
          : "border-white/90 shadow-emerald-100";

  const cardWidth =
    authMode === "login"
      ? "max-w-[430px]"
      : "max-w-[560px]";

  return (
    <section className="flex h-dvh w-screen shrink-0 snap-center items-center justify-center px-5 pb-6 pt-28 sm:px-8 lg:px-12">
      <div
        className={`mx-auto grid w-full items-center gap-8 ${
          authMode === "login"
            ? "max-w-6xl lg:grid-cols-[0.95fr_0.9fr]"
            : "max-w-6xl lg:grid-cols-[0.9fr_1fr]"
        }`}
      >
        <div className="hidden rounded-[1.9rem] border border-white/80 bg-white/62 p-7 shadow-[0_24px_70px_rgba(15,118,110,0.12)] backdrop-blur-2xl lg:block">
          <p className="text-xs font-black uppercase tracking-[0.26em] text-emerald-700">
            {authMode === "login" ? "Start Now" : "Join Now"}
          </p>

          <h2 className="mt-4 max-w-xl text-4xl font-black leading-[0.94] tracking-[-0.055em] text-slate-950 xl:text-5xl">
            {copy.title}
          </h2>

          <p className="mt-4 max-w-md text-sm font-semibold leading-7 text-slate-600 xl:text-base">
            {copy.subtitle}
          </p>
        </div>

        <div
          className={`relative mx-auto w-full ${cardWidth} overflow-hidden rounded-[2rem] border bg-white/88 p-5 shadow-[0_28px_80px_rgba(15,118,110,0.18)] backdrop-blur-2xl transition-all duration-300 sm:p-6 ${stateClass}`}
        >
          <div className="pointer-events-none absolute -right-20 -top-20 h-40 w-40 rounded-full bg-emerald-200/50 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-24 left-8 h-44 w-44 rounded-full bg-lime-200/35 blur-3xl" />

          <div className="relative">
            <div
              className={`flex items-start justify-between gap-4 ${
                authMode === "login" ? "mb-5" : "mb-4"
              }`}
            >
              <div>
                <div
                  className={`inline-flex items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-600 to-lime-400 text-white shadow-[0_14px_34px_rgba(16,185,129,0.35)] ${
                    authMode === "login"
                      ? "mb-4 h-11 w-11"
                      : "mb-3 h-10 w-10"
                  }`}
                >
                  <Sparkles className="h-5 w-5" />
                </div>

                <p className="text-[0.65rem] font-black uppercase tracking-[0.24em] text-emerald-700">
                  {authMode === "login"
                    ? "GreenSprint Login"
                    : "GreenSprint Register"}
                </p>

                <h3
                  className={`mt-2 font-black leading-none tracking-[-0.045em] text-slate-950 ${
                    authMode === "login"
                      ? "text-[1.7rem]"
                      : "text-[1.55rem]"
                  }`}
                >
                  {authMode === "login"
                    ? "Welcome back"
                    : "Create account"}
                </h3>
              </div>

              <span className="mt-1 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1 text-[0.65rem] font-black uppercase tracking-[0.16em] text-emerald-700">
                Secure
              </span>
            </div>

            <p
              className={`text-sm font-semibold leading-6 text-slate-500 ${
                authMode === "login"
                  ? "-mt-2 mb-5"
                  : "mb-4"
              }`}
            >
              {authMode === "login"
                ? "Continue to missions, AI verification, rewards, community, and impact reports."
                : "Join GreenSprint to complete verified eco missions and earn rewards."}
            </p>

            {authMode === "login" ? (
              <LoginForm
                onVisualStateChange={(state) =>
                  onVisualStateChange(state)
                }
                onSwitchToRegister={() =>
                  onAuthModeChange("register")
                }
              />
            ) : (
              <RegisterForm
                onVisualStateChange={(state) =>
                  onVisualStateChange(state)
                }
                onSwitchToLogin={() =>
                  onAuthModeChange("login")
                }
              />
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function getLoginCopy(state: LoginVisualState) {
  if (state === "email") {
    return {
      title: "Find your GreenSprint profile.",
      subtitle:
        "Enter your email to continue to your sustainability dashboard.",
    };
  }

  if (state === "password") {
    return {
      title: "Secure your impact journey.",
      subtitle:
        "Your submissions, rewards, badges, and impact progress stay protected.",
    };
  }

  if (state === "loading") {
    return {
      title: "Verifying your identity.",
      subtitle:
        "GreenSprint is connecting your account, rewards, and dashboard.",
    };
  }

  if (state === "error") {
    return {
      title: "Let’s try again.",
      subtitle:
        "Check your details and continue your GreenSprint journey.",
    };
  }

  if (state === "success") {
    return {
      title: "Welcome back.",
      subtitle:
        "Your dashboard, missions, and rewards are getting ready.",
    };
  }

  return {
    title: "Start your GreenSprint journey.",
    subtitle:
      "Login or create an account to begin completing verified eco missions.",
  };
}

function getRegisterCopy(state: RegisterVisualState) {
  if (state === "name") {
    return {
      title: "Tell us who you are.",
      subtitle:
        "Your profile name will be used across missions, rewards, and community activity.",
    };
  }

  if (state === "email") {
    return {
      title: "Create your GreenSprint identity.",
      subtitle:
        "Use an email address to access your account and verified progress.",
    };
  }

  if (state === "role") {
    return {
      title: "Choose your account type.",
      subtitle:
        "Users complete missions, while organizations can create campaigns and reports.",
    };
  }

  if (state === "password" || state === "confirm") {
    return {
      title: "Secure your account.",
      subtitle:
        "Use a strong password to protect your profile, rewards, and impact data.",
    };
  }

  if (state === "loading") {
    return {
      title: "Creating your account.",
      subtitle:
        "GreenSprint is preparing your profile and sustainability journey.",
    };
  }

  if (state === "error") {
    return {
      title: "Let’s fix that.",
      subtitle:
        "Check the details and try creating your GreenSprint account again.",
    };
  }

  if (state === "success") {
    return {
      title: "Account created.",
      subtitle:
        "You can now login and start completing verified eco missions.",
    };
  }

  return {
    title: "Start your GreenSprint journey.",
    subtitle:
      "Create an account to begin completing verified eco missions and tracking real impact.",
  };
}