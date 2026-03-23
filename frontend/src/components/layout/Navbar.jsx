import { Bell, Menu, Search } from "lucide-react";
import { Link } from "react-router-dom";

import { useAppContext } from "../../context/AppContext";

export function Navbar({ onMenuToggle }) {
  const { profile } = useAppContext();

  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-white/10 bg-ink/75 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-4 md:px-6">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuToggle}
            className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-200 hover:bg-white/10 lg:hidden"
          >
            <Menu size={18} />
          </button>
          <Link to="/" className="font-display text-xl tracking-[0.22em] text-white">
            MYET AI
          </Link>
        </div>
        <div className="hidden max-w-xl flex-1 items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 md:flex">
          <Search size={16} className="text-slate-400" />
          <span className="text-sm text-slate-400">Search stories, sectors, or companies</span>
        </div>
        <div className="flex items-center gap-3">
          <button className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-200 hover:bg-white/10">
            <Bell size={18} />
          </button>
          <Link to="/profile" className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100">
            {profile?.role ?? "Profile"}
          </Link>
        </div>
      </div>
    </header>
  );
}
