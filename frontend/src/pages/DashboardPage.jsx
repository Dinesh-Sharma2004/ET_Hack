import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import { NewsCard } from "../components/cards/NewsCard";
import { Button } from "../components/ui/Button";
import { Loader } from "../components/ui/Loader";
import { SkeletonCard } from "../components/ui/SkeletonCard";

export default function DashboardPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.getDashboard().then(setData);
  }, []);

  if (!data) {
    return (
      <div className="space-y-6">
        <Loader label="Loading dashboard" />
        <div className="grid gap-4 md:grid-cols-3">
          <SkeletonCard className="h-32" />
          <SkeletonCard className="h-32" />
          <SkeletonCard className="h-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-white/10 bg-[linear-gradient(135deg,rgba(15,118,110,0.22),rgba(7,16,24,0.58))] p-7 shadow-glow">
        <p className="text-xs uppercase tracking-[0.35em] text-teal-200">Home / Dashboard</p>
        <div className="mt-5 grid gap-6 lg:grid-cols-[1.3fr_0.8fr]">
          <div>
            <h1 className="font-display text-5xl leading-tight text-white">
              Business news that behaves like an intelligence product.
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-8 text-slate-200">
              MyET AI gives you a clean, personalized command center for signal-rich stories, market context, and next-step exploration.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link to="/my-news">
                <Button>Open My Newsroom</Button>
              </Link>
              <Link to="/videos">
                <Button variant="secondary">Watch AI videos</Button>
              </Link>
            </div>
          </div>
          <div className="rounded-[28px] border border-white/10 bg-black/20 p-5">
            <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Your lens</p>
            <div className="mt-4 space-y-3 text-sm text-slate-200">
              <p>Role: {data.profile.role}</p>
              <p>Interests: {data.profile.interests.join(", ")}</p>
              <p>Portfolio: {data.profile.portfolio_symbols.join(", ")}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {data.highlights.map((metric) => (
          <div key={metric.label} className="rounded-[28px] border border-white/10 bg-white/6 p-5">
            <div className="text-sm text-slate-400">{metric.label}</div>
            <div className="mt-3 font-display text-4xl text-white">{metric.value}</div>
            <div className="mt-2 text-sm text-teal-100">{metric.delta}</div>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-4">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-slate-500">For You</p>
              <h2 className="mt-2 font-display text-3xl">Personalized feed</h2>
            </div>
            <Link to="/my-news" className="text-sm text-teal-200 hover:text-white">
              See all
            </Link>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            {data.feed.map((card) => (
              <article key={card.article_id} className="rounded-[28px] border border-white/10 bg-white/6 p-5">
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.25em] text-slate-400">
                  <span>{card.category}</span>
                  <span>{Math.round(card.relevance_score * 100)}% match</span>
                </div>
                <h3 className="mt-4 font-display text-2xl text-white">{card.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-300">{card.summary}</p>
                <p className="mt-4 rounded-2xl bg-white/5 px-4 py-3 text-sm text-teal-100">{card.why_it_matters}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-xs uppercase tracking-[0.32em] text-slate-500">Trending</p>
            <h2 className="mt-2 font-display text-3xl">Fast-moving business arcs</h2>
          </div>
          <div className="space-y-4">
            {data.trending.map((article) => (
              <NewsCard key={article.id} article={article} compact />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
