"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/providers/AuthProvider";
import GreenGuide from "./GreenGuide";

interface Props {
  onContinue: () => void;
}

export default function WelcomeExperience({ onContinue }: Props) {
  const { user } = useAuth();

  const [lines, setLines] = useState<string[]>([]);
  const [currentLine, setCurrentLine] = useState("");
  const [lineIndex, setLineIndex] = useState(0);
  const [showMission, setShowMission] = useState(false);
  const [showContinue, setShowContinue] = useState(false);

  const displayName = user?.full_name || "User";

  const messages = [
    "Initializing synchronized telemetry...",
    "Your sustainability activities are being tracked successfully.",
    "You currently have environmental initiatives in progress.",
    "Today's active objective is ready to begin.",
  ];

  useEffect(() => {
    if (lineIndex >= messages.length) {
      setTimeout(() => {
        setShowMission(true);
        setTimeout(() => {
          setShowContinue(true);
        }, 500);
      }, 300);
      return;
    }

    const message = messages[lineIndex];
    let charIndex = 0;
    setCurrentLine("");

    const interval = setInterval(() => {
      if (charIndex < message.length) {
        setCurrentLine((prev) => prev + message[charIndex]);
        charIndex++;
      } else {
        clearInterval(interval);
        setLines((prev) => [...prev, message]);
        setCurrentLine("");
        setTimeout(() => {
          setLineIndex((prev) => prev + 1);
        }, 600);
      }
    }, 20);

    return () => clearInterval(interval);
  }, [lineIndex]);

  return (
    <div className="preview-root relative min-h-screen w-full overflow-y-auto bg-[#020705] text-slate-100 font-sans custom-scrollbar block select-none">
      
      {/* Immersive Cinematic Screen Gradients */}
      <div className="absolute inset-0 z-0 pointer-events-none fixed">
        <div
          className="absolute inset-0 bg-cover bg-center scale-105 opacity-35 mix-blend-color-dodge"
          style={{
            backgroundImage: "url('/images/dashboard-forest.webp')",
          }}
        />
        <div className="absolute inset-0 bg-[#020705]/10 z-10" />
        <div className="absolute inset-0 bg-gradient-to-tr from-[#010403] via-[#030907]/10 to-[#010302]/10" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/30 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/60" />
      </div>

      {/* Main Structural Layout Grid */}
      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-[1600px] items-center px-6 sm:px-12 lg:px-16 pt-10 pb-16 box-border">
        
        {/* Left Section: Character Anchor */}
        <div className="hidden lg:flex w-[32%] items-end justify-center pb-24 self-stretch">
          <div className="sticky bottom-0 w-full flex justify-center transform translate-y-[-30px]">
            <GreenGuide />
          </div>
        </div>

        {/* Right Section: Gateway Core Briefing Layout */}
        <div className="w-full lg:w-[68%] lg:pl-16 max-w-[720px] flex flex-col h-auto min-h-max justify-center items-start pt-10 box-border">
          
          {/* Top Authentication Notification */}
          <div className="flex items-center gap-3 font-mono font-bold text-[11px] tracking-[0.25em] text-[#49E29D] flex-shrink-0">
            <span className="h-1.5 w-1.5 rounded-full bg-[#49E29D] animate-pulse" />
            SECURE ACCESS GRANTED // ESTABLISHING LINK
          </div>

          {/* Hero Title */}
          <h1 className="mt-4 text-5xl sm:text-6xl lg:text-[76px] font-black tracking-tighter leading-none text-white uppercase italic">
            Welcome <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#49E29D] via-[#A6F2CE] to-white">{displayName}</span>
          </h1>

          {/* Command Terminal Typelog Logs */}
          <div className="relative mt-8 pl-6 w-full max-w-[620px]">
            <div className="absolute left-0 top-1 bottom-1 w-[2px] bg-gradient-to-b from-[#49E29D] via-[#112d20] to-transparent" />
            
            <div className="flex flex-col gap-3.5">
              {lines.map((line, index) => {
                const isFirstLine = index === 0;
                const isLastLine = index === messages.length - 1 && !currentLine;
                
                return (
                  <p
                    key={index}
                    className={`text-[16px] sm:text-[17px] font-mono tracking-wide transition-all duration-300
                      ${isFirstLine 
                        ? "text-[#49E29D] font-bold drop-shadow-[0_0_10px_rgba(73,226,157,0.5)]" 
                        : isLastLine 
                          ? "text-white opacity-100 font-bold drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]" 
                          : "text-[#A7F3D0] font-medium drop-shadow-[0_0_4px_rgba(167,243,208,0.1)]" // UPDATED: Light high-contrast mint color override
                      }`}
                  >
                    &gt; {line}
                  </p>
                );
              })}

              {currentLine && (
                <p className={`text-[16px] sm:text-[17px] font-mono tracking-wide font-bold ${lines.length === 0 ? "text-[#49E29D]" : "text-white"}`}>
                  &gt; {currentLine}
                  <span className="inline-block bg-[#49E29D] ml-1.5 h-4.5 w-2 translate-y-0.5 animate-[blink_0.9s_step-end_infinite]" />
                </p>
              )}
            </div>
          </div>

          {/* IMMERSIVE MISSION BRIEFING PANEL */}
          {showMission && (
            <div className="briefing-panel-entry relative mt-12 w-full flex flex-col gap-8 border-t border-[#143528]/40 pt-8">
              
              {/* Objective Summary Header */}
              <div className="flex flex-col gap-2 pl-6 py-1">
                <span className="text-[11px] font-mono font-bold tracking-[0.35em] text-[#49E29D] uppercase">
                  PRIMARY OBJECTIVE
                </span>
                <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-wide leading-none text-white uppercase tracking-tight">
                  Plant 10 Trees
                </h2>
                <p className="text-[15px] sm:text-[16px] leading-relaxed text-[#E2F7ED] font-semibold max-w-[560px] mt-4">
                  Take part in today's sustainability mission and help grow verified environmental impact.
                </p>
              </div>

              {/* Mission Column Row Alignment */}
              <div className="flex flex-wrap items-center justify-between gap-y-4 font-mono py-2 w-full max-w-[620px] pl-6">
                
                {/* Expected Reward */}
                <div className="flex flex-col gap-1 min-w-[150px]">
                  <span className="text-[10px] text-[#49E29D] font-bold tracking-wider uppercase">EXPECTED REWARD</span>
                  <span className="text-2xl font-black text-[#FFD65A] tracking-tight drop-shadow-[0_2px_8px_rgba(255,214,90,0.15)]">+500 GP</span>
                </div>

                <div className="w-[1px] h-8 bg-[#1B4232] hidden sm:block mx-2" />

                {/* Sector */}
                <div className="flex flex-col gap-1 min-w-[150px]">
                  <span className="text-[10px] text-[#49E29D] font-bold tracking-wider uppercase">SECTOR</span>
                  <span className="text-[14px] font-extrabold text-white tracking-wide uppercase">TREE PLANTATION</span>
                </div>

                <div className="w-[1px] h-8 bg-[#1B4232] hidden sm:block mx-2" />

                {/* Target Status */}
                <div className="flex flex-col gap-1 min-w-[150px]">
                  <span className="text-[10px] text-[#49E29D] font-bold tracking-wider uppercase">TARGET STATUS</span>
                  <span className="text-[13px] font-extrabold text-[#49E29D] flex items-center gap-2 drop-shadow-[0_0_6px_rgba(73,226,157,0.3)]">
                    <span className="h-2 w-2 rounded-full bg-[#49E29D] animate-pulse" /> READY TO INITIATE
                  </span>
                </div>

              </div>

              {/* Transparent Journey CTA */}
              {showContinue && (
                <div className="w-full pt-4 mt-2 pl-6">
                  <button
                    onClick={onContinue}
                    className="relative overflow-hidden h-[54px] w-full min-w-[300px] max-w-[340px] rounded-lg font-mono font-bold text-xs sm:text-sm tracking-[0.18em] text-[#49E29D] bg-transparent border border-[#49E29D]/40 shadow-[0_0_15px_rgba(73,226,157,0.05)] hover:text-white hover:border-[#49E29D] hover:shadow-[0_0_30px_rgba(73,226,157,0.3)] transition-all duration-300 ease-out group cursor-pointer uppercase flex items-center justify-center gap-3"
                  >
                    <div className="absolute inset-0 bg-[#49E29D]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#49E29D]/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.8s_ease-in-out_infinite]" />
                    
                    <span className="relative z-10 flex items-center gap-2">
                      Continue Your Journey
                      <svg className="w-4 h-4 transform group-hover:translate-x-1.5 transition-transform duration-300 stroke-[2.5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </span>
                  </button>
                </div>
              )}

            </div>
          )}
        </div>
      </div>

      {/* Global Framework UI Core Keyframes */}
      <style jsx global>{`
        @keyframes blink {
          50% { opacity: 0; }
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes briefingSlideIn {
          from {
            opacity: 0;
            transform: translateY(16px);
            filter: blur(2px) brightness(1.5);
          }
          to {
            opacity: 1;
            transform: translateY(0);
            filter: blur(0) brightness(1);
          }
        }
        .briefing-panel-entry {
          animation: briefingSlideIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #020705;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #112d20;
          border-radius: 99px;
        }
      `}</style>
    </div>
  );
}