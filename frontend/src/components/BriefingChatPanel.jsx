import { useState } from "react";

import { api } from "../api/client";
import { GlassCard } from "./ui/GlassCard";

export function BriefingChatPanel({ prompts }) {
  const [question, setQuestion] = useState(prompts[0] ?? "");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const result = await api.askBriefing({ question, mode: "expert", history: [] });
      setResponse(result);
    } finally {
      setLoading(false);
    }
  }

  return (
    <GlassCard className="space-y-5">
      <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-300">Navigator Chat</p>
      <textarea
        className="min-h-28 w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-4 text-sm text-white outline-none"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
      />
      <div className="flex flex-wrap gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => setQuestion(prompt)}
            className="rounded-full border border-white/10 px-3 py-2 text-xs text-slate-200 hover:bg-white/5"
          >
            {prompt}
          </button>
        ))}
      </div>
      <button onClick={ask} className="rounded-2xl bg-white px-4 py-3 font-semibold text-ink">
        {loading ? "Thinking..." : "Ask MyET AI"}
      </button>
      {response ? (
        <div className="space-y-4 rounded-3xl bg-white/5 p-5">
          <p className="text-sm leading-7 text-slate-200">{response.answer}</p>
          <div className="text-xs uppercase tracking-[0.25em] text-slate-400">Sources</div>
          <div className="space-y-2 text-sm text-teal-100">
            {response.supporting_articles.map((item) => (
              <p key={item}>{item}</p>
            ))}
          </div>
        </div>
      ) : null}
    </GlassCard>
  );
}
