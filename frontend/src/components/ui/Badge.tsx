interface Props {
  children: React.ReactNode;
}

export default function Badge({
  children,
}: Props) {
  return (
    <span
      className="
      inline-flex
      items-center
      rounded-full
      border
      border-emerald-200
      bg-emerald-50
      px-3
      py-1
      text-xs
      font-medium
      text-emerald-700
    "
    >
      {children}
    </span>
  );
}