import { useEffect, useState } from "react";

import { api } from "../api/client";
import { VideoCard } from "../components/cards/VideoCard";
import { Loader } from "../components/ui/Loader";

export default function VideosPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.getVideos().then(setData);
  }, []);

  if (!data) return <Loader label="Loading videos" />;

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-white/10 bg-white/6 p-7">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-500">/videos</p>
        <h1 className="mt-3 font-display text-4xl">AI Video Studio</h1>
        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-300">
          Browse generated explainers, each built from article summaries, narrative scripts, charts, and related reporting.
        </p>
      </section>
      <section className="grid gap-4 xl:grid-cols-3">
        {data.items.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </section>
    </div>
  );
}
