export function SectionHeader({ eyebrow, title, description, action }) {
  return (
    <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div className="max-w-2xl">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-accent/80">{eyebrow}</p>
        <h2 className="mt-2 font-display text-3xl font-bold text-white md:text-4xl">{title}</h2>
        <p className="mt-2 text-sm leading-7 text-slate-300 md:text-base">{description}</p>
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}
