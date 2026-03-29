import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api/client";
import { NewsCard } from "../components/cards/NewsCard";
import { Loader } from "../components/ui/Loader";

export default function StoryPage() {
  const { id = "AI infrastructure" } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.getStory(id).then(setData);
  }, [id]);

  if (!data) return <Loader label="Loading story arc" />;

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-white/10 bg-white/6 p-7">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-500">/story/{id}</p>
        <h1 className="mt-3 font-display text-4xl">{data.arc.theme}</h1>
        <p className="mt-4 text-sm leading-8 text-slate-300">
          Follow the evolving coverage timeline, entity map, and AI-generated outlook to understand where the story is heading next.
        </p>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-[28px] border border-white/10 bg-black/20 p-5">
          <div className="text-xs uppercase tracking-[0.28em] text-slate-500">Timeline</div>
          <div className="mt-5 space-y-4">
            {data.arc.timeline.map((point) => (
              <div key={`${point.date}-${point.headline}`} className="rounded-3xl border border-white/10 p-4">
                <div className="text-xs uppercase tracking-[0.24em] text-slate-500">{point.date}</div>
                <h2 className="mt-2 text-lg text-white">{point.headline}</h2>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-6">
          <div className="rounded-[28px] border border-white/10 bg-white/6 p-5">
            <div className="text-xs uppercase tracking-[0.28em] text-slate-500">Entity graph</div>
            <div className="mt-5 flex flex-wrap gap-3">
              {data.arc.entities.map((node) => (
                <div key={node.id} className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200">
                  {node.label}
                </div>
              ))}
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {data.arc.relationships.slice(0, 8).map((edge, index) => (
                <div key={`${edge.source}-${edge.target}-${index}`} className="rounded-2xl bg-black/20 px-4 py-3 text-sm text-slate-300">
                  {edge.source} ↔ {edge.target}
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-[28px] border border-white/10 bg-white/6 p-5">
            <div className="text-xs uppercase tracking-[0.28em] text-slate-500">AI reading</div>
            <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
              <p>
                This view focuses on how the story is developing across coverage, who is involved, and what the AI expects
                users to watch next.
              </p>
              <p>
                Use the connected entities and related reporting to move deeper into the narrative without switching into
                analytics-heavy views.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-[28px] border border-white/10 bg-white/6 p-5">
          <div className="text-xs uppercase tracking-[0.28em] text-slate-500">What next</div>
          <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
            {data.arc.what_next.map((item) => (
              <p key={item}>{item}</p>
            ))}
          </div>
        </div>
        <div className="space-y-4">
          {data.related_articles.map((article) => (
            <NewsCard key={article.id} article={article} compact />
          ))}
        </div>
      </section>
    </div>
  );
}
