import { useEffect, useState } from "react";
import { Check, Database, KeyRound, Palette, Save, ShieldCheck, Trash2, Volume2 } from "lucide-react";
import { api } from "../api";
import { useApp } from "../app-context";
import Tag from "../components/Tag";

const THEMES = [
  { id: "aurora", label: "极光 Aurora", desc: "青蓝 + 紫罗兰，冷静的未来感。" },
  { id: "neon", label: "霓虹 Neon", desc: "青色 + 品红，赛博夜城。" },
  { id: "ember", label: "余烬 Ember", desc: "琥珀 + 玫瑰，温暖但危险。" },
  { id: "mono", label: "单色 Mono", desc: "银白 + 石墨，极简终端。" },
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
  const [dataset, setDataset] = useState<{ summary: Record<string, unknown>; preview: Array<Record<string, unknown>> } | null>(null);

  useEffect(() => {
    void api.dataset().then(setDataset);
  }, []);

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
          <div className="eyebrow mono"><span className="pulse-dot" /> CONTROL ROOM</div>
          <h1>设置</h1>
          <p className="page-lead">
            模型、密钥、主题和本地数据。所有敏感信息只保存在本机用户数据目录。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">SECURITY</span>
          <strong className="security-badge"><ShieldCheck size={18} /> LOCAL</strong>
        </div>
      </header>

      <div className="settings-grid">
        <section className="glass settings-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">MODEL GATEWAY</div>
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
              <div className="section-label mono">VOICE LAYER</div>
              <h2>语音</h2>
            </div>
            <Volume2 size={20} className="accent" />
          </div>
          <p className="muted small">
            v1 默认使用浏览器语音合成。GPT-SoVITS 适配器保留接口；填入本地服务地址后会在后续版本启用。
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
              <div className="section-label mono">THEME MATRIX</div>
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

        <section className="glass settings-panel dataset-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">STYLE DATASET</div>
              <h2>文本数据集</h2>
            </div>
            <Database size={20} className="accent" />
          </div>
          {dataset ? (
            <>
              <div className="dataset-stats">
                <div><strong>{String(dataset.summary.works || 0)}</strong><span>作品</span></div>
                <div><strong>{String(dataset.summary.version || "v0.1")}</strong><span>版本</span></div>
                <div><strong>{String(dataset.summary.status || "ready")}</strong><span>状态</span></div>
              </div>
              <div className="dataset-list">
                {dataset.preview.slice(0, 6).map((work, index) => (
                  <div key={index} className="dataset-row">
                    <span className="mono">{String(work.id || index)}</span>
                    <strong>{String(work.title_zh || work.title || "未命名")}</strong>
                    <Tag tone="accent">{String((work.genres as string[])?.[0] || "VN")}</Tag>
                  </div>
                ))}
              </div>
              <p className="mono micro muted">
                数据集只收录剧情摘要、结构分析与来源链接；不直接打包游戏资源。
              </p>
            </>
          ) : (
            <p className="muted">正在读取数据集...</p>
          )}
        </section>
      </div>
    </div>
  );
}

