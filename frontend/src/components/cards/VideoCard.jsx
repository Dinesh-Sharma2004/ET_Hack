import { Link } from "react-router-dom";

export function VideoCard({ video }) {
  return (
    <Link
      to={`/video/${video.id}`}
      className="block rounded-[28px] border border-white/10 bg-white/6 p-5 shadow-glow backdrop-blur-xl transition hover:-translate-y-1 hover:bg-white/10"
    >
      <div className="text-xs uppercase tracking-[0.25em] text-slate-400">{video.category}</div>
      <h3 className="mt-4 font-display text-2xl text-white">{video.title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-300">{video.summary}</p>
      <div className="mt-5 text-sm text-teal-100">{video.runtime_seconds}s runtime</div>
    </Link>
  );
}
