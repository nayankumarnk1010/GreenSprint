import { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement>;

export default function Button({
  className = "",
  ...props
}: Props) {
  return (
    <button
      {...props}
      className={`
        h-12
        rounded-2xl
        px-6
        font-medium
        text-white

        bg-emerald-500
        hover:bg-emerald-600

        transition-all
        duration-300

        shadow-lg
        shadow-emerald-500/20

        hover:-translate-y-0.5

        disabled:opacity-50

        ${className}
      `}
    />
  );
}