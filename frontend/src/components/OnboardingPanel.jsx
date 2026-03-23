import { useState } from "react";

import { api } from "../api/client";
import { GlassCard } from "./ui/GlassCard";

export function OnboardingPanel({ profile, onProfileChange, onRecommendations }) {
  const [role, setRole] = useState(profile.role);
  const [interests, setInterests] = useState(profile.interests.join(", "));
  const [sectors, setSectors] = useState(profile.sectors.join(", "));
  const [languages, setLanguages] = useState(profile.languages.join(", "));
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      const nextProfile = await api.saveProfile({
        role,
        interests: interests.split(",").map((item) => item.trim()).filter(Boolean),
        sectors: sectors.split(",").map((item) => item.trim()).filter(Boolean),
        languages: languages.split(",").map((item) => item.trim()).filter(Boolean),
        risk_appetite: profile.risk_appetite,
        portfolio_symbols: profile.portfolio_symbols,
        onboarding_completed: true
      });
      onProfileChange(nextProfile);
    } finally {
      setSaving(false);
    }
  }

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const result = await api.uploadPortfolio(file);
    onRecommendations(result);
  }

  return (
    <GlassCard className="border-white/10 bg-black/20">
      <p className="text-sm uppercase tracking-[0.3em] text-slate-400">User Lens</p>
      <div className="mt-4 grid gap-3">
        <label className="text-sm text-slate-300">
          Role
          <input
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none"
            value={role}
            onChange={(event) => setRole(event.target.value)}
          />
        </label>
        <label className="text-sm text-slate-300">
          Interests
          <input
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none"
            value={interests}
            onChange={(event) => setInterests(event.target.value)}
          />
        </label>
        <label className="text-sm text-slate-300">
          Sectors
          <input
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none"
            value={sectors}
            onChange={(event) => setSectors(event.target.value)}
          />
        </label>
        <label className="text-sm text-slate-300">
          Languages
          <input
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none"
            value={languages}
            onChange={(event) => setLanguages(event.target.value)}
          />
        </label>
      </div>
      <div className="mt-6 grid gap-3">
        <button
          onClick={handleSave}
          className="rounded-2xl bg-accent px-5 py-3 font-semibold text-white transition hover:bg-teal-500"
        >
          {saving ? "Saving..." : "Rebuild My Feed"}
        </button>
        <label className="rounded-2xl border border-white/10 px-5 py-3 text-center font-semibold text-white transition hover:bg-white/5">
          Upload Portfolio CSV
          <input type="file" accept=".csv" className="hidden" onChange={handleUpload} />
        </label>
      </div>
    </GlassCard>
  );
}
