import { ReactNode } from "react";

interface Props {
  children: ReactNode;
  className?: string;
}

export default function Card({
  children,
  className = "",
}: Props) {
  return (
    <div
      className={`
        rounded-3xl
        border
        border-white/40
        bg-white/70
        backdrop-blur-xl

        shadow-xl
        shadow-slate-200/50

        ${className}
      `}
    >
      {children}
    </div>
  );
}