import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api/client";
import { NewsCard } from "../components/cards/NewsCard";
import { Loader } from "../components/ui/Loader";

export default function VideoDetailPage() {
  const { id = "video-art-001" } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.getVideo(id).then(setData);
  }, [id]);

  if (!data) return <Loader label="Loading video detail" />;

  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <div className="rounded-[32px] border border-white/10 bg-white/6 p-7">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">/video/{id}</p>
          <h1 className="mt-3 font-display text-4xl">{data.detail.title}</h1>
          {data.video_url ? (
            <video
              controls
              className="mt-5 aspect-video w-full rounded-[28px] border border-white/10 bg-black"
              src={data.video_url}
            />
          ) : (
            <div className="mt-5 aspect-video rounded-[28px] border border-white/10 bg-[linear-gradient(135deg,rgba(15,118,110,0.18),rgba(9,21,33,0.8))] p-6">
              <div className="text-sm text-slate-300">Video generation in progress</div>
              <div className="mt-4 font-display text-3xl text-white">{data.detail.runtime_seconds}s narrative cut</div>
              <div className="mt-3 text-sm leading-7 text-slate-300">
                Designed for FFmpeg stitching, subtitles, charts, and TTS-driven production output.
              </div>
            </div>
          )}
        </div>
        <div className="rounded-[32px] border border-white/10 bg-black/20 p-7">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Key highlights</p>
          <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
            {data.key_highlights.map((item) => (
              <p key={item}>{item}</p>
            ))}
          </div>
          <p className="mt-6 text-xs uppercase tracking-[0.28em] text-slate-500">Script</p>
          <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
            {data.script.map((line, index) => (
              <p key={`${index}-${line}`}>{line}</p>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.detail.segments.map((segment) => (
          <div key={segment.scene} className="rounded-[28px] border border-white/10 bg-white/6 p-5">
            <div className="text-xs uppercase tracking-[0.25em] text-slate-500">{segment.duration_seconds}s</div>
            <h2 className="mt-3 font-display text-2xl">{segment.scene}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-300">{segment.visual}</p>
          </div>
        ))}
      </section>

      <section className="space-y-4">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-slate-500">Related articles</p>
          <h2 className="mt-2 font-display text-3xl">Supporting reporting</h2>
        </div>
        <div className="grid gap-4">
          {data.related_articles.map((article) => (
            <NewsCard key={article.id} article={article} compact />
          ))}
        </div>
      </section>
    </div>
  );
}
