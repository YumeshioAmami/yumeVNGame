import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Check,
  Image,
  KeyRound,
  Music,
  Package,
  Palette,
  Save,
  ShieldCheck,
  Volume2,
} from "lucide-react";
import { api } from "../api";
import { useApp } from "../app-context";
import AgentConfigCard from "../components/AgentConfigCard";
import type { AgentCategory, AgentConfig } from "../types";

const THEMES = [
  { id: "morning", label: "晨光 Morning", desc: "奶油白、浅杏、淡紫。最温柔的一档。" },
  { id: "sakura", label: "樱雾 Sakura", desc: "樱花粉、雾紫、奶白。轻软、亲近。" },
  { id: "mint", label: "薄荷 Mint", desc: "薄荷绿、天空蓝、奶油黄。清爽、安静。" },
  { id: "night", label: "夜灯 Night", desc: "深紫、暖粉、灯光黄。适合夜里慢慢看。" },
];

const AGENT_SECTIONS: Array<{
  id: AgentCategory;
  label: string;
  eyebrow: string;
  icon: typeof Image;
}> = [
  { id: "image", label: "图像 Agent", eyebrow: "IMAGE AGENTS", icon: Image },
  { id: "text", label: "文本 Agent", eyebrow: "TEXT AGENTS", icon: KeyRound },
  { id: "music", label: "音乐 Agent", eyebrow: "MUSIC AGENTS", icon: Music },
];

export default function Settings() {
  const { data, refresh, theme, setTheme } = useApp();
  const [ttsEndpoint, setTtsEndpoint] = useState(data.settings.tts_endpoint);
  const [ttsVoice, setTtsVoice] = useState(data.settings.tts_voice);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [agentsLoading, setAgentsLoading] = useState(true);
  const [agentsError, setAgentsError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    api.agentConfigs()
      .then((result) => {
        if (alive) setAgents(result.agents);
      })
      .catch((err) => {
        if (alive) setAgentsError(err instanceof Error ? err.message : "读取 Agent 配置失败");
      })
      .finally(() => {
        if (alive) setAgentsLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  async function saveSettings() {
    setBusy(true);
    setMessage(null);
    try {
      await api.updateSettings({
        tts_endpoint: ttsEndpoint,
        tts_voice: ttsVoice,
        theme,
      });
      setMessage("界面与语音设置已保存。");
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  function handleAgentSaved(saved: AgentConfig) {
    setAgents((current) => current.map((agent) => (agent.id === saved.id ? saved : agent)));
  }

  return (
    <div className="page settings-page">
      <header className="page-head">
        <div>
          <div className="eyebrow mono"><span className="pulse-dot" /> COZY CONTROL ROOM</div>
          <h1>设置</h1>
          <p className="page-lead">
            按分工配置模型。每个 Agent 都可以独立选择 API 或本地模式；配置写入本地数据库，API Key 加密保存。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">PRIVACY</span>
          <strong className="security-badge"><ShieldCheck size={18} /> LOCAL</strong>
        </div>
      </header>

      <div className="settings-grid">
        {AGENT_SECTIONS.map((section) => {
          const Icon = section.icon;
          const items = agents.filter((agent) => agent.category === section.id);
          return (
            <section className="glass settings-panel agent-section" key={section.id}>
              <div className="panel-head">
                <div>
                  <div className="section-label mono">{section.eyebrow}</div>
                  <h2>{section.label}</h2>
                </div>
                <Icon size={20} className="accent" />
              </div>
              <p className="muted small">
                每个分工独立配置模型名、服务地址、Key 和本地文件。切换模式不会丢失另一侧的配置。
              </p>
              {agentsError && <div className="settings-message">{agentsError}</div>}
              {agentsLoading ? (
                <p className="muted small">正在读取本地配置...</p>
              ) : (
                <div className="agent-config-grid">
                  {items.map((config) => (
                    <AgentConfigCard key={config.id} config={config} onSaved={handleAgentSaved} />
                  ))}
                </div>
              )}
            </section>
          );
        })}

        <section className="glass settings-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">VOICE</div>
              <h2>语音</h2>
            </div>
            <Volume2 size={20} className="accent" />
          </div>
          <p className="muted small">
            默认使用浏览器语音合成。GPT-SoVITS 适配器保留在本机，填入本地服务地址后即可尝试。
          </p>
          <label className="field">
            <span>GPT-SoVITS Endpoint</span>
            <input
              value={ttsEndpoint}
              onChange={(event) => setTtsEndpoint(event.target.value)}
              placeholder="http://127.0.0.1:9880"
            />
          </label>
          <label className="field">
            <span>音色 / Voice ID</span>
            <input
              value={ttsVoice}
              onChange={(event) => setTtsVoice(event.target.value)}
              placeholder="任意已有音色"
            />
          </label>
          <div className="tts-note">
            <Volume2 size={16} />
            <span>播放器右上角的朗读按钮当前使用浏览器 TTS。</span>
          </div>
        </section>

        <section className="glass settings-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">THEME</div>
              <h2>界面主题</h2>
            </div>
            <Palette size={20} className="accent" />
          </div>
          <div className="theme-cards">
            {THEMES.map((item) => (
              <button
                key={item.id}
                className={`theme-card theme-${item.id} ${theme === item.id ? "active" : ""}`}
                onClick={() => setTheme(item.id)}
              >
                <span className="theme-preview" />
                <strong>{item.label}</strong>
                <em>{item.desc}</em>
                {theme === item.id && <Check size={16} />}
              </button>
            ))}
          </div>
          <button className="btn btn-primary" onClick={() => void saveSettings()} disabled={busy}>
            <Save size={15} /> 保存界面与语音设置
          </button>
          {message && <div className="settings-message"><Check size={15} /> {message}</div>}
        </section>

        <section className="glass settings-panel plugin-link-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">CONTENT PACKS</div>
              <h2>插件与数据集</h2>
            </div>
            <Package size={20} className="accent" />
          </div>
          <p className="muted small">
            数据集、世界包、故事包、音乐、图片、语音和素材包都在独立插件页管理。
          </p>
          <div className="dataset-stats">
            <div><strong>{data.dataset.active_plugins || 0}</strong><span>启用插件</span></div>
            <div><strong>{data.dataset.works || 0}</strong><span>作品样本</span></div>
            <div><strong>EXTERNAL</strong><span>数据模式</span></div>
          </div>
          <Link to="/plugins" className="btn btn-primary">
            <Package size={15} /> 打开插件页 <ArrowRight size={15} />
          </Link>
        </section>
      </div>
    </div>
  );
}
