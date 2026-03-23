export function Loader({ label = "Loading", fullPage = false }) {
  return (
    <div className={`${fullPage ? "flex min-h-screen" : "flex min-h-[220px]"} items-center justify-center`}>
      <div className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm tracking-[0.28em] text-slate-300">
        {label}
      </div>
    </div>
  );
}
