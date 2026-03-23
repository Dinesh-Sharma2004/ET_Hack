import { ArrowRight, Clock3 } from "lucide-react";
import { Link } from "react-router-dom";

export function NewsCard({ article, compact = false }) {
  const storyLink = `/story/${encodeURIComponent(article.category === "AI" ? "AI infrastructure" : article.category)}`;
  return (
    <article className="rounded-[28px] border border-white/10 bg-white/6 p-5 shadow-glow backdrop-blur-xl transition hover:-translate-y-1 hover:bg-white/10">
      <div className="flex items-center justify-between text-xs uppercase tracking-[0.25em] text-slate-400">
        <span>{article.category}</span>
        <span className="inline-flex items-center gap-2">
          <Clock3 size={14} />
          {article.read_time_minutes} min
        </span>
      </div>
      <h3 className="mt-4 font-display text-2xl leading-tight text-white">{article.title}</h3>
      <p className={`mt-3 text-slate-300 ${compact ? "line-clamp-3 text-sm" : "text-sm leading-7"}`}>
        {article.summary}
      </p>
      <div className="mt-5 flex flex-wrap gap-2">
        {article.entities.slice(0, 3).map((entity) => (
          <span key={entity} className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-300">
            {entity}
          </span>
        ))}
      </div>
      <div className="mt-5 flex gap-3 text-sm">
        <Link to={storyLink} className="inline-flex items-center gap-2 text-teal-200 hover:text-white">
          Open story <ArrowRight size={16} />
        </Link>
        <Link to={`/briefing/${encodeURIComponent(article.category.toLowerCase())}`} className="text-slate-300 hover:text-white">
          Open briefing
        </Link>
      </div>
    </article>
  );
}
