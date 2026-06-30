"use client";

import Image from "next/image";
import { useEffect, useMemo, useState } from "react";

export default function LivingTreeBackground() {
  const [position, setPosition] = useState({
    x: 0,
    y: 0,
  });

  const particles = useMemo(() => {
    return Array.from({ length: 75 }).map((_, index) => ({
      id: index,
      size: 2 + (index % 4),
      left: (index * 17) % 100,
      delay: index * 0.22,
      duration: 12 + (index % 11),
      opacity: 0.25 + (index % 5) * 0.08,
    }));
  }, []);

  const leaves = useMemo(() => {
    return Array.from({ length: 12 }).map((_, index) => ({
      id: index,
      left: (index * 23) % 100,
      delay: index * 1.4,
      duration: 18 + (index % 8),
      size: 9 + (index % 5),
    }));
  }, []);

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (window.innerWidth < 768) return;

      const x = (event.clientX / window.innerWidth - 0.5) * 18;
      const y = (event.clientY / window.innerHeight - 0.5) * 18;

      setPosition({
        x,
        y,
      });
    };

    window.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden bg-slate-950">
      {/* Background image with soft parallax */}
      <div
        className="absolute inset-[-24px] transition-transform duration-700 ease-out"
        style={{
          transform: `translate(${position.x}px, ${position.y}px) scale(1.06)`,
        }}
      >
        <div className="tree-breath absolute inset-0">
          <Image
            src="/assets/branding/tree-master.webp"
            alt="GreenSprint living forest background"
            fill
            priority
            sizes="100vw"
            className="object-cover object-center"
          />
        </div>
      </div>

      {/* Deep cinematic overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-slate-950/95 via-slate-950/70 to-slate-950/90" />
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950/40 via-transparent to-slate-950/95" />

      {/* Tree depth vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_38%_38%,transparent_0%,rgba(2,6,23,0.28)_34%,rgba(2,6,23,0.9)_100%)]" />

      {/* Living emerald glow around tree */}
      <div
        className="absolute left-[30%] top-[28%] h-[520px] w-[520px] rounded-full bg-emerald-400/14 blur-[130px] transition-transform duration-700"
        style={{
          transform: `translate(${position.x * 0.45}px, ${position.y * 0.45}px)`,
        }}
      />

      <div className="gs-aurora absolute right-[8%] top-[18%] h-[440px] w-[440px] rounded-full bg-emerald-500/10 blur-[120px]" />

      {/* Light beam */}
      <div className="beam-sweep absolute left-[43%] top-[-20%] h-[130vh] w-[260px] rotate-[19deg] bg-gradient-to-b from-emerald-200/0 via-emerald-200/10 to-emerald-200/0 blur-3xl" />

      {/* Moving fog */}
      <div className="living-fog absolute bottom-[-12%] left-[-10%] h-[45vh] w-[120vw] rounded-full bg-slate-200/8 blur-[70px]" />
      <div className="living-fog-slow absolute bottom-[8%] right-[-18%] h-[35vh] w-[90vw] rounded-full bg-emerald-200/5 blur-[80px]" />

      {/* Ecosystem nodes */}
      <span className="pulse-glow absolute left-[18%] top-[24%] h-2.5 w-2.5 rounded-full bg-emerald-300 shadow-[0_0_26px_rgba(52,211,153,0.95)]" />
      <span className="pulse-glow-delayed absolute left-[43%] top-[44%] h-3 w-3 rounded-full bg-lime-300 shadow-[0_0_30px_rgba(190,242,100,0.8)]" />
      <span className="pulse-glow absolute right-[22%] top-[31%] h-2 w-2 rounded-full bg-emerald-200 shadow-[0_0_22px_rgba(167,243,208,0.8)]" />
      <span className="pulse-glow-delayed absolute right-[13%] bottom-[18%] h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_26px_rgba(52,211,153,0.85)]" />

      {/* Floating fireflies */}
      <div className="absolute inset-0">
        {particles.map((particle) => (
          <span
            key={particle.id}
            className="particle absolute bottom-[-20px] rounded-full bg-emerald-200"
            style={{
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              left: `${particle.left}%`,
              opacity: particle.opacity,
              animationDelay: `${particle.delay}s`,
              animationDuration: `${particle.duration}s`,
              boxShadow: "0 0 16px rgba(110, 231, 183, 0.9)",
            }}
          />
        ))}
      </div>

      {/* Tiny falling leaves / organic motion */}
      <div className="absolute inset-0">
        {leaves.map((leaf) => (
          <span
            key={leaf.id}
            className="leaf-drift absolute top-[-40px] rounded-full bg-emerald-300/20"
            style={{
              width: `${leaf.size}px`,
              height: `${leaf.size * 0.45}px`,
              left: `${leaf.left}%`,
              animationDelay: `${leaf.delay}s`,
              animationDuration: `${leaf.duration}s`,
            }}
          />
        ))}
      </div>

      {/* Fine texture */}
      <div
        className="absolute inset-0 opacity-[0.04] mix-blend-overlay"
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
      />

      {/* Soft shimmer */}
      <div className="ecosystem-shimmer absolute inset-0" />
    </div>
  );
}