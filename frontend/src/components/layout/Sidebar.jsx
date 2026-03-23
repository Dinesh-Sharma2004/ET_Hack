import { Film, Globe2, Home, Sparkles, User2, Waypoints } from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/my-news", label: "My News", icon: Sparkles },
  { to: "/briefing/ai", label: "Briefing", icon: Sparkles },
  { to: "/story/AI infrastructure", label: "Story Arc", icon: Waypoints },
  { to: "/videos", label: "Videos", icon: Film },
  { to: "/vernacular", label: "Vernacular", icon: Globe2 },
  { to: "/profile", label: "Profile", icon: User2 }
];

export function Sidebar({ collapsed }) {
  return (
    <aside
      className={`sticky top-24 hidden h-[calc(100vh-7rem)] shrink-0 rounded-[28px] border border-white/10 bg-black/20 p-4 backdrop-blur-xl lg:block ${
        collapsed ? "w-24" : "w-72"
      }`}
    >
      <div className="mb-5 px-3 text-xs uppercase tracking-[0.35em] text-slate-500">Navigate</div>
      <nav className="space-y-2">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition ${
                isActive ? "bg-accent text-white" : "text-slate-300 hover:bg-white/6 hover:text-white"
              }`
            }
          >
            <Icon size={18} />
            {!collapsed ? <span>{label}</span> : null}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
