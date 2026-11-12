import { useCallback, useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AppContext } from "./app-context";
import { api } from "./api";
import type { Bootstrap } from "./types";
import Shell from "./components/Shell";
import Home from "./pages/Home";
import Library from "./pages/Library";
import Create from "./pages/Create";
import Player from "./pages/Player";
import Gallery from "./pages/Gallery";
import Settings from "./pages/Settings";

export default function App() {
  const [data, setData] = useState<Bootstrap | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [theme, setThemeState] = useState(
    () => localStorage.getItem("yume-theme") || "aurora",
  );

  const setTheme = useCallback((next: string) => {
    setThemeState(next);
    localStorage.setItem("yume-theme", next);
  }, []);

  const refresh = useCallback(async () => {
    try {
      const next = await api.bootstrap();
      setData(next);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法连接本地后端");
    }
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  if (error) {
    return (
      <div className="boot-screen">
        <div className="boot-panel">
          <div className="brand-mark">Y//</div>
          <h1>本地运行时未连接</h1>
          <p>{error}</p>
          <p className="mono muted">请先运行 npm run dev，或检查 8787 端口。</p>
          <button className="btn btn-primary" onClick={() => void refresh()}>
            重新连接
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="boot-screen">
        <div className="boot-orb" />
        <div className="boot-copy">
          <div className="brand-mark">Y//</div>
          <h1>正在唤醒世界线</h1>
          <p className="mono muted">BOOTING LOCAL NARRATIVE CORE...</p>
          <div className="boot-line"><span /></div>
        </div>
      </div>
    );
  }

  return (
    <AppContext.Provider value={{ data, refresh, theme, setTheme }}>
      <Shell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/library" element={<Library />} />
          <Route path="/create" element={<Create />} />
          <Route path="/play/:storyId" element={<Player />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/gallery/:storyId" element={<Gallery />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Shell>
    </AppContext.Provider>
  );
}

