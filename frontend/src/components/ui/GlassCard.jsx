export function GlassCard({ className = "", children }) {
  return (
    <div
      className={`rounded-[28px] border border-white/10 bg-white/6 p-6 shadow-glow backdrop-blur-xl ${className}`}
    >
      {children}
    </div>
  );
}
