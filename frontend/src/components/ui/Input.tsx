import { InputHTMLAttributes } from "react";

type Props = InputHTMLAttributes<HTMLInputElement>;

export default function Input({
  className = "",
  ...props
}: Props) {
  return (
    <input
      {...props}
      className={`
        h-12
        w-full

        rounded-2xl

        border
        border-slate-200

        bg-white/80

        px-4

        outline-none

        transition

        focus:border-emerald-500
        focus:ring-4
        focus:ring-emerald-100

        ${className}
      `}
    />
  );
}