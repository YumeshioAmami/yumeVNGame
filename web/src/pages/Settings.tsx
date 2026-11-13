import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Check,
  KeyRound,
  Package,
  Palette,
  Save,
  ShieldCheck,
  Trash2,
  Volume2,
} from "lucide-react";
import { api } from "../api";
import { useApp } from "../app-context";

const THEMES = [
  { id: "morning", label: "晨光 Morning", desc: "奶油白、浅杏、淡紫。最温柔的一档。" },
  { id: "sakura", label: "樱雾 Sakura", desc: "樱花粉、雾紫、奶白。轻软、亲近。" },
  { id: "mint", label: "薄荷 Mint", desc: "薄荷绿、天空蓝、奶油黄。清爽、安静。" },
  { id: "night", label: "夜灯 Night", desc: "深紫、暖粉、灯光黄。适合夜里慢慢看。" },
];

export default function Settings() {
  const { data, refresh, theme, setTheme } = useApp();
  const [keyInput, setKeyInput] = useState("");
  const [model, setModel] = useState(data.settings.model);
  const [baseUrl, setBaseUrl] = useState(data.settings.base_url);
  const [ttsEndpoint, setTtsEndpoint] = useState(data.settings.tts_endpoint);
  const [ttsVoice, setTtsVoice] = useState(data.settings.tts_voice);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function saveKey() {
    if (!keyInput.trim()) {
      setMessage("请输入 API Key。");
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const result = await api.setSecret(keyInput.trim(), model, baseUrl);
      setKeyInput("");
      setMessage(`已加密保存：${result.secrets.masked_key}`);
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  async function clearKey() {
    setBusy(true);
    try {
      await api.clearSecret();
      setMessage("已删除本地 API Key。");
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function saveSettings() {
    setBusy(true);
    setMessage(null);
    try {
      await api.updateSettings({
        model,
        base_url: baseUrl,
        tts_endpoint: ttsEndpoint,
        tts_voice: ttsVoice,
        theme,
      });
      setMessage("设置已保存。");
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page settings-page">
      <header className="page-head">
        <div>
          <div className="eyebrow mono"><span className="pulse-dot" /> COZY CONTROL ROOM</div>
          <h1>设置</h1>
          <p className="page-lead">
            模型、密钥、主题和声音。所有敏感信息都只留在这台电脑上。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">PRIVACY</span>
          <strong className="security-badge"><ShieldCheck size={18} /> LOCAL</strong>
        </div>
      </header>

      <div className="settings-grid">
        <section className="glass settings-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">TEXT MODEL</div>
              <h2>文本模型</h2>
            </div>
            <KeyRound size={20} className="accent" />
          </div>

          <div className="secret-status">
            <span className={`status-dot ${data.secrets.has_api_key ? "online" : "warn"}`} />
            <span>{data.secrets.has_api_key ? "已配置加密密钥" : "尚未配置密钥"}</span>
            {data.secrets.has_api_key && <code>{data.secrets.masked_key}</code>}
          </div>

          <label className="field">
            <span>DeepSeek API Key</span>
            <input
              type="password"
              value={keyInput}
              onChange={(event) => setKeyInput(event.target.value)}
              placeholder="sk-..."
              autoComplete="off"
            />
          </label>
          <div className="field-row">
            <label className="field">
              <span>模型名</span>
              <input value={model} onChange={(event) => setModel(event.target.value)} />
            </label>
            <label className="field">
              <span>Base URL</span>
              <input value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} />
            </label>
          </div>
          <div className="button-row">
            <button className="btn btn-primary" onClick={() => void saveKey()} disabled={busy}>
              <Save size={15} /> 加密保存 Key
            </button>
            {data.secrets.has_api_key && (
              <button className="btn btn-danger" onClick={() => void clearKey()} disabled={busy}>
                <Trash2 size={15} /> 删除 Key
              </button>
            )}
          </div>
          <p className="mono micro muted">
            Fernet 加密 · {data.secrets.storage}
          </p>
        </section>

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
            <Save size={15} /> 保存设置
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

