import { useEffect, useState } from "react";

import { api } from "../api/client";
import { useAppContext } from "../context/AppContext";
import { Button } from "../components/ui/Button";
import { Loader } from "../components/ui/Loader";
import { Modal } from "../components/ui/Modal";

export default function ProfilePage() {
  const { profile, setProfile } = useAppContext();
  const [form, setForm] = useState(null);
  const [portfolioResult, setPortfolioResult] = useState(null);

  useEffect(() => {
    if (profile) {
      setForm({
        ...profile,
        interests: profile.interests.join(", "),
        sectors: profile.sectors.join(", "),
        languages: profile.languages.join(", ")
      });
    }
  }, [profile]);

  if (!form) return <Loader label="Loading profile" />;

  async function handleSave() {
    const payload = {
      role: form.role,
      interests: form.interests.split(",").map((item) => item.trim()).filter(Boolean),
      sectors: form.sectors.split(",").map((item) => item.trim()).filter(Boolean),
      languages: form.languages.split(",").map((item) => item.trim()).filter(Boolean),
      risk_appetite: form.risk_appetite,
      portfolio_symbols: profile.portfolio_symbols,
      onboarding_completed: true
    };
    const updated = await api.updateProfile(payload);
    setProfile(updated);
  }

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const response = await api.uploadPortfolio(file);
    setProfile(response.profile);
    setPortfolioResult(response);
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-white/10 bg-white/6 p-7">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-500">/profile</p>
        <h1 className="mt-3 font-display text-4xl">User profile and preferences</h1>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <div className="rounded-[32px] border border-white/10 bg-black/20 p-7">
          <div className="grid gap-4">
            {[
              ["Role", "role"],
              ["Interests", "interests"],
              ["Sectors", "sectors"],
              ["Languages", "languages"],
              ["Risk appetite", "risk_appetite"]
            ].map(([label, key]) => (
              <label key={key} className="text-sm text-slate-300">
                {label}
                <input
                  value={form[key]}
                  onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-[#102030] px-4 py-3 text-white outline-none"
                />
              </label>
            ))}
          </div>
          <div className="mt-5 flex gap-3">
            <Button onClick={handleSave}>Save preferences</Button>
            <label className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:bg-white/10">
              Upload portfolio CSV
              <input type="file" accept=".csv" className="hidden" onChange={handleUpload} />
            </label>
          </div>
        </div>
        <div className="rounded-[32px] border border-white/10 bg-white/6 p-7">
          <div className="text-xs uppercase tracking-[0.28em] text-slate-500">Current profile</div>
          <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
            <p>Portfolio symbols: {profile?.portfolio_symbols?.join(", ")}</p>
            <p>Languages: {profile?.languages?.join(", ")}</p>
            <p>Interests: {profile?.interests?.join(", ")}</p>
          </div>
        </div>
      </section>

      <Modal open={Boolean(portfolioResult)} title="Portfolio recommendations" onClose={() => setPortfolioResult(null)}>
        <div className="space-y-3 text-sm leading-7 text-slate-200">
          {portfolioResult?.items.map((item) => (
            <p key={item.article_id}>{item.title}</p>
          ))}
        </div>
      </Modal>
    </div>
  );
}
