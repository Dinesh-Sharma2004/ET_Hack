import { useEffect, useState } from "react";

import { api } from "../api/client";
import { Button } from "../components/ui/Button";
import { Loader } from "../components/ui/Loader";

const languages = ["Hindi", "Tamil", "Telugu", "Bengali"];

export default function VernacularPage() {
  const [language, setLanguage] = useState("Hindi");
  const [mode, setMode] = useState("contextual");
  const [translation, setTranslation] = useState(null);

  useEffect(() => {
    api.translate({ article_id: "art-001", language, mode }).then(setTranslation);
  }, [language, mode]);

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-white/10 bg-white/6 p-7">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-500">/vernacular</p>
        <h1 className="mt-3 font-display text-4xl">Multilingual News</h1>
        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-300">
          Adapt business reporting for regional audiences with a clear literal-versus-contextual toggle.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          {languages.map((item) => (
            <Button
              key={item}
              variant={item === language ? "primary" : "secondary"}
              onClick={() => setLanguage(item)}
            >
              {item}
            </Button>
          ))}
        </div>
        <div className="mt-4 flex gap-3">
          <Button variant={mode === "literal" ? "primary" : "secondary"} onClick={() => setMode("literal")}>
            Literal
          </Button>
          <Button variant={mode === "contextual" ? "primary" : "secondary"} onClick={() => setMode("contextual")}>
            Contextual
          </Button>
        </div>
      </section>

      {!translation ? (
        <Loader label="Translating article" />
      ) : (
        <section className="rounded-[32px] border border-white/10 bg-black/20 p-7">
          <div className="text-xs uppercase tracking-[0.28em] text-slate-500">
            {translation.language} / {translation.mode}
          </div>
          <h2 className="mt-3 font-display text-3xl">{translation.title}</h2>
          <p className="mt-4 text-base leading-8 text-slate-200">{translation.content}</p>
        </section>
      )}
    </div>
  );
}
