export function Modal({ open, title, children, onClose }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/70 p-4">
      <div className="w-full max-w-2xl rounded-[28px] border border-white/10 bg-[#0c1824] p-6 shadow-glow">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-2xl text-white">{title}</h3>
          <button onClick={onClose} className="text-sm text-slate-400 hover:text-white">
            Close
          </button>
        </div>
        <div className="mt-5">{children}</div>
      </div>
    </div>
  );
}
