import { useState } from "react";

import { api } from "../../api/client";
import { Button } from "../ui/Button";

export function ChatPanel({ topic, prompts = [] }) {
  const [question, setQuestion] = useState(prompts[0] ?? "");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    setLoading(true);
    try {
      const payload = await api.askBriefing(topic, { question, mode: "expert", history: [] });
      setAnswer(payload.response);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-[28px] border border-white/10 bg-black/20 p-5 shadow-glow backdrop-blur-xl">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Follow-up chat</p>
      <textarea
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        className="mt-4 min-h-32 w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-4 text-sm text-white outline-none"
      />
      <div className="mt-4 flex flex-wrap gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => setQuestion(prompt)}
            className="rounded-full border border-white/10 px-3 py-2 text-xs text-slate-300 hover:bg-white/8"
          >
            {prompt}
          </button>
        ))}
      </div>
      <Button className="mt-4 w-full" onClick={handleAsk}>
        {loading ? "Thinking..." : "Ask MyET AI"}
      </Button>
      {answer ? (
        <div className="mt-5 space-y-3 rounded-3xl bg-white/5 p-4">
          <p className="text-sm leading-7 text-slate-200">{answer.answer}</p>
          <div className="text-xs uppercase tracking-[0.28em] text-slate-500">Supporting articles</div>
          {answer.supporting_articles.map((item) => (
            <p key={item} className="text-sm text-teal-100">
              {item}
            </p>
          ))}
        </div>
      ) : null}
    </div>
  );
}
