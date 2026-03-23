export function Button({ children, className = "", variant = "primary", ...props }) {
  const styles =
    variant === "secondary"
      ? "border border-white/10 bg-white/5 text-white hover:bg-white/10"
      : "bg-accent text-white hover:bg-teal-500";
  return (
    <button className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${styles} ${className}`} {...props}>
      {children}
    </button>
  );
}
