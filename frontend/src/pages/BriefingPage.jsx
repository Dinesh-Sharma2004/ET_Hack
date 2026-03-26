import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api/client";
import { ChatPanel } from "../components/chat/ChatPanel";
import { NewsCard } from "../components/cards/NewsCard";
import { Loader } from "../components/ui/Loader";

export default function BriefingPage() {
  const { topic = "ai" } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.getBriefing(topic).then(setData);
  }, [topic]);

  if (!data) return <Loader label="Loading briefing" />;

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <section className="space-y-6">
        <div className="rounded-[32px] border border-white/10 bg-white/6 p-7">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">/briefing/{topic}</p>
          <h1 className="mt-3 font-display text-4xl">{data.report.headline}</h1>
          <p className="mt-4 text-sm leading-8 text-slate-300">{data.report.summary}</p>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          {data.report.insights.map((section) => (
            <div key={section.title} className="rounded-[28px] border border-white/10 bg-black/20 p-5">
              <h2 className="font-display text-2xl">{section.title}</h2>
              <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                {section.bullets.map((item) => (
                  <p key={item}>{item}</p>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-[28px] border border-white/10 bg-white/6 p-5">
            <div className="text-xs uppercase tracking-[0.28em] text-coral">Risks</div>
            <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
              {data.report.risks.map((item) => (
                <p key={item}>{item}</p>
              ))}
            </div>
          </div>
          <div className="rounded-[28px] border border-white/10 bg-white/6 p-5">
            <div className="text-xs uppercase tracking-[0.28em] text-teal-200">Opportunities</div>
            <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
              {data.report.opportunities.map((item) => (
                <p key={item}>{item}</p>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-xs uppercase tracking-[0.32em] text-slate-500">Related articles</p>
            <h2 className="mt-2 font-display text-3xl">Read the surrounding signals</h2>
          </div>
          <div className="grid gap-4">
            {data.related_articles.map((article) => (
              <NewsCard key={article.id} article={article} compact />
            ))}
          </div>
        </div>
      </section>

      <aside className="space-y-6">
        <ChatPanel topic={topic} prompts={data.suggested_questions} />
      </aside>
    </div>
  );
}
