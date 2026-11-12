import type { ReactNode } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  Home,
  Library,
  Wand2,
  Images,
  Settings,
  ShieldCheck,
  Cpu,
  Sparkles,
} from "lucide-react";
import { useApp } from "../app-context";

const NAV = [
  { to: "/", label: "总览", icon: Home },
  { to: "/library", label: "故事库", icon: Library },
  { to: "/create", label: "创作", icon: Wand2 },
  { to: "/gallery", label: "回廊", icon: Images },
  { to: "/settings", label: "设置", icon: Settings },
];

const THEMES = [
  { id: "aurora", label: "极光" },
  { id: "neon", label: "霓虹" },
  { id: "ember", label: "余烬" },
  { id: "mono", label: "单色" },
];

export default function Shell({ children }: { children: ReactNode }) {
  const { data, theme, setTheme } = useApp();
  const location = useLocation();
  const isPlayer = location.pathname.startsWith("/play");

  return (
    <div className={`app-shell ${isPlayer ? "player-mode" : ""}`}>
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="ambient ambient-c" />
      <div className="grid-overlay" />
      <div className="noise-overlay" />

      <aside className="sidebar glass">
        <div className="brand">
          <div className="brand-mark">Y//</div>
          <div>
            <div className="brand-name">yumeVNGame</div>
            <div className="mono brand-sub">AI VISUAL NOVEL RUNTIME</div>
          </div>
        </div>

        <nav className="nav">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                <span className="nav-spark" />
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-section">
          <div className="section-label mono">THEME MATRIX</div>
          <div className="theme-grid">
            {THEMES.map((item) => (
              <button
                key={item.id}
                className={`theme-chip theme-${item.id} ${theme === item.id ? "active" : ""}`}
                onClick={() => setTheme(item.id)}
                aria-label={item.label}
              >
                <span className="theme-dot" />
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-section runtime-card">
          <div className="runtime-row">
            <Cpu size={15} />
            <span>LOCAL CORE</span>
            <span className="status-dot online" />
          </div>
          <div className="runtime-row">
            <ShieldCheck size={15} />
            <span>{data.secrets.has_api_key ? "KEY ENCRYPTED" : "KEY MISSING"}</span>
            <span className={`status-dot ${data.secrets.has_api_key ? "online" : "warn"}`} />
          </div>
          <div className="runtime-row">
            <Sparkles size={15} />
            <span>{data.dataset.works || 0} STYLE WORKS</span>
          </div>
          <div className="runtime-meter">
            <span style={{ width: `${Math.min(100, (data.stats.gallery_unlocks || 0) * 4 + 18)}%` }} />
          </div>
          <div className="mono micro muted">LOCAL-FIRST / NO CLOUD SYNC</div>
        </div>

        <div className="sidebar-footer mono">
          <span>v1.0.0</span>
          <span>MIT</span>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}

