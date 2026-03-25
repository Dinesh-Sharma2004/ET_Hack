import { useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { NewsCard } from "../components/cards/NewsCard";
import { Loader } from "../components/ui/Loader";
import { SkeletonCard } from "../components/ui/SkeletonCard";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";

const PAGE_SIZE = 2;

export default function MyNewsPage() {
  const [filters, setFilters] = useState({ industry: "", stock: "", interest: "", search: "" });
  const [recommendations, setRecommendations] = useState(null);
  const [newsPage, setNewsPage] = useState({ items: [], total: 0 });
  const [offset, setOffset] = useState(0);
  const debouncedSearch = useDebouncedValue(filters.search);

  useEffect(() => {
    api.getRecommendations({
      industry: filters.industry,
      stock: filters.stock,
      interest: filters.interest
    }).then(setRecommendations);
  }, [filters.industry, filters.interest, filters.stock]);

  useEffect(() => {
    setOffset(0);
    api
      .getNews({
        category: filters.industry,
        stock: filters.stock,
        interest: filters.interest,
        search: debouncedSearch,
        offset: 0,
        limit: PAGE_SIZE
      })
      .then((payload) => setNewsPage({ items: payload.items, total: payload.total }));
  }, [debouncedSearch, filters.industry, filters.interest, filters.stock]);

  const canLoadMore = newsPage.items.length < newsPage.total;
  const sentinelRef = useInfiniteScroll(() => {
    if (!canLoadMore) return;
    const nextOffset = offset + PAGE_SIZE;
    api
      .getNews({
        category: filters.industry,
        stock: filters.stock,
        interest: filters.interest,
        search: debouncedSearch,
        offset: nextOffset,
        limit: PAGE_SIZE
      })
      .then((payload) => {
        setOffset(nextOffset);
        setNewsPage((current) => ({ ...payload, items: [...current.items, ...payload.items] }));
      });
  }, canLoadMore);

  const options = useMemo(() => recommendations?.filters ?? { industries: [], stocks: [], interests: [] }, [recommendations]);

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-white/10 bg-white/6 p-7">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-500">/my-news</p>
        <h1 className="mt-3 font-display text-4xl">Personalized Newsroom</h1>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">
          Filter by industry, tracked stocks, or interests and scroll through a deeper feed shaped by your profile.
        </p>
        <div className="mt-6 grid gap-3 lg:grid-cols-4">
          <select
            value={filters.industry}
            onChange={(event) => setFilters((current) => ({ ...current, industry: event.target.value }))}
            className="rounded-2xl border border-white/10 bg-[#102030] px-4 py-3 text-sm text-white"
          >
            <option value="">All industries</option>
            {options.industries.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
          <select
            value={filters.stock}
            onChange={(event) => setFilters((current) => ({ ...current, stock: event.target.value }))}
            className="rounded-2xl border border-white/10 bg-[#102030] px-4 py-3 text-sm text-white"
          >
            <option value="">All stocks</option>
            {options.stocks.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
          <select
            value={filters.interest}
            onChange={(event) => setFilters((current) => ({ ...current, interest: event.target.value }))}
            className="rounded-2xl border border-white/10 bg-[#102030] px-4 py-3 text-sm text-white"
          >
            <option value="">All interests</option>
            {options.interests.slice(0, 10).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
          <input
            value={filters.search}
            onChange={(event) => setFilters((current) => ({ ...current, search: event.target.value }))}
            placeholder="Search signals"
            className="rounded-2xl border border-white/10 bg-[#102030] px-4 py-3 text-sm text-white outline-none"
          />
        </div>
      </section>

      {!recommendations ? <Loader label="Loading recommendations" /> : null}
      <section className="grid gap-4 lg:grid-cols-3">
        {recommendations?.items.slice(0, 3).map((item) => (
          <article key={item.article_id} className="rounded-[28px] border border-white/10 bg-black/20 p-5">
            <div className="text-xs uppercase tracking-[0.28em] text-slate-500">{item.category}</div>
            <h2 className="mt-3 font-display text-2xl">{item.title}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-300">{item.why_it_matters}</p>
          </article>
        ))}
      </section>

      <section className="space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.32em] text-slate-500">Infinite Feed</p>
            <h2 className="mt-2 font-display text-3xl">Deeper signal stream</h2>
          </div>
          <div className="text-sm text-slate-400">{newsPage.items.length} of {newsPage.total} loaded</div>
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          {newsPage.items.map((article) => (
            <NewsCard key={article.id} article={article} />
          ))}
          {!newsPage.items.length ? <SkeletonCard className="h-64 xl:col-span-2" /> : null}
        </div>
        <div ref={sentinelRef} className="h-8" />
      </section>
    </div>
  );
}
