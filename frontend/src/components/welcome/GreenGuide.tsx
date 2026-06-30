"use client";

import Image from "next/image";
import { motion } from "framer-motion";

export default function GreenGuide() {
  return (
    <motion.div
      animate={{
        y: [-4, 4, -4],
      }}
      transition={{
        duration: 7,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      className="
        relative
        flex
        items-end
        justify-center
      "
    >
      {/* Outer ambient glow — wide, very soft */}
      <div
        className="
          absolute
          bottom-8
          h-[320px]
          w-[320px]
          rounded-full
        "
        style={{
          background:
            "radial-gradient(circle, rgba(73,226,157,0.08) 0%, transparent 70%)",
          filter: "blur(48px)",
        }}
      />

      {/* Inner ground glow — tight, brighter */}
      <div
        className="
          absolute
          bottom-6
          h-[120px]
          w-[200px]
          rounded-full
        "
        style={{
          background:
            "radial-gradient(ellipse, rgba(73,226,157,0.18) 0%, transparent 75%)",
          filter: "blur(28px)",
        }}
      />

      {/* Elliptical ground shadow — grounds the character */}
      <div
        className="
          absolute
          bottom-2
          h-[18px]
          w-[130px]
          rounded-full
        "
        style={{
          background:
            "radial-gradient(ellipse, rgba(73,226,157,0.22) 0%, transparent 100%)",
          filter: "blur(10px)",
        }}
      />

      <Image
        src="/guides/green-guide-welcome.png"
        alt="Green Guide"
        width={500}
        height={900}
        priority
        className="
          relative
          z-10
          h-auto
          w-full
          max-w-[260px]
          object-contain
        "
        style={{
          filter:
            "drop-shadow(0 28px 48px rgba(0,0,0,0.45)) drop-shadow(0 0 40px rgba(73,226,157,0.12))",
        }}
      />
    </motion.div>
  );
}